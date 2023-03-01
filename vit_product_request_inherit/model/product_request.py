#!/usr/bin/python
#-*- coding: utf-8 -*-

STATES = [('draft', 'Draft'), ('open', 'Open'), ('done','Done')]
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import random

class product_request(models.Model):
    _name = "vit.product_request"
    _inherit = "vit.product_request"
    

    @api.model
    def create(self, vals):
        if not vals.get("name", False) or vals["name"] == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("vit.product_request") or "Error Number!!!"

            rd = random.randint(1000,9999)
            vals["name"] = vals["name"] + str(rd)

        return super(product_request, self).create(vals)

    def action_confirm(self):
        self.state = STATES[1][0]

    def action_done(self):
        self.state = STATES[2][0]

    def action_draft(self):
        self.state = STATES[0][0]

    def unlink(self):
        for me_id in self :
            if me_id.state != STATES[0][0]:
                raise UserError("Cannot delete non draft record!")
        return super(product_request, self).unlink()

    def action_create_transfer(self):
        import pandas
        # cari wh_int picking type
        wh_int = self.env['stock.picking.type'].search([
            ('sequence_code','=','INT'),
            ('warehouse_id.code','=','WH2'),
        ])

        # siapkan details
        uom = self.env['uom.uom'].search([('name','=','Units')])
        details = [(0,0,{
            'product_id' : x.product_id.id, #product template
            'product_uom_qty': x.quantity,
            'name':x.product_id.name,
            'product_uom': uom.id, # units
            'location_id': wh_int.default_location_src_id.id,
            'location_dest_id': self.location_dest_id.id,
        }) for x in self.detail_ids] #list array

        # create record transfer (stock.picking)
        self.env['stock.picking'].create({
            'picking_type_id': wh_int.id, # picking type WH utama
            'location_id': wh_int.default_location_src_id.id, #source location
            'location_dest_id': self.location_dest_id.id,
            'origin': self.name,
            'move_ids_without_package': details, # one2many
            'product_request_id': self.id,
        })


        # update qty moved here


    def action_create_rfq(self):
        
        # mencari partner vendor utk PO
        partner = self.env['res.partner'].search( [], limit=1 )

        # mencari picking type
        picking = self.env['stock.picking.type'].search([
            ('name','=','Receipts'),('warehouse_id.code','=','WH')
        ])

        #order lines, copy dari details product request
        order_line = [ (0,0,{
            'product_id'  : line.product_id.id,
            'name'        : line.product_id.name,
            'product_qty' : line.quantity,
            'price_unit'  : line.product_id.standard_price,
        }) for line in self.detail_ids]
        
        # create record PO (rfq)
        self.env['purchase.order'].create({
            'partner_id' : partner.id, #field id / PK
            'date_order' : fields.Datetime.now(),
            'picking_type_id': picking.id,
            'origin': self.name,
            'order_line': order_line,
        })

        # update qty po here



    transfer_count = fields.Integer( string="Transfer count", compute="_get_transfer_count")
    po_count = fields.Integer( string="PO count", compute="_get_po_count")



    def _get_transfer_count(self):
        for x in self:
            x.transfer_count = len(self.transfer_ids)




    def action_view_transfer(self):

        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        pickings = self.mapped('transfer_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)] # filter supaya hanya picking yg id nya berada di transfer_ids product_request
        elif pickings: # ==1 
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
            
        return action


    def _get_po_count(self):
        for x in self:
            x.po_count = len(self.po_ids)




    def action_view_po(self):

        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        pos = self.mapped('po_ids')
        if len(pos) > 1:
            action['domain'] = [('id', 'in', pos.ids)] # filter supaya hanya po yg id nya berada di po_ids product_request
        elif pos: # ==1 
            action['views'] = [(self.env.ref('purchase.view_po_form').id, 'form')]
            action['res_id'] = pos.id
            
        return action