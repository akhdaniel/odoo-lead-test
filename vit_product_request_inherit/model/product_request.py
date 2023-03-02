#!/usr/bin/python
#-*- coding: utf-8 -*-

import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError

STATES = [('draft', 'Draft'), ('open', 'Open'), ('done','Done')]

class product_request(models.Model):
    _inherit = "vit.product_request"
    
    @api.model
    def create(self, vals):
        """ Override the create button to add a 4-digit new random """
        if not vals.get("name", False) or vals["name"] == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("vit.product_request") or "Error Number!!!"
            rd = random.randint(1000,9999)
            vals["name"] = vals["name"] + str(rd)
        return super(product_request, self).create(vals)

    def action_create_transfer(self):
        """ Function to create the pickings related to this request """
        # cari wh_int picking type
        wh_int = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id.code','=','WH'),
        ])
        # siapkan details
        details = [(0,0,{
            'product_id' : x.product_id.id, #product template
            'product_uom_qty': x.quantity,
            'name':x.product_id.name,
            'product_uom': x.product_id.uom_id.id, # units
            'location_id': wh_int.default_location_src_id.id,
            'location_dest_id': self.location_dest_id.id,
        }) for x in self.detail_ids] #list array
        # create record transfer (stock.picking)
        picking = self.env['stock.picking'].create({
            'picking_type_id': wh_int.id, # picking type WH utama
            'location_id': wh_int.default_location_src_id.id, #source location
            'location_dest_id': self.location_dest_id.id,
            'origin': self.name,
            'move_ids_without_package': details, # one2many
            'product_request_id': self.id,
        })
        # update the qty moved
        for record in self.detail_ids:
            move_ids = self.env['stock.move'].search([
                ('product_id', '=', record.product_id.id),
                ('picking_id', '=', picking.id),
            ])
            for move in move_ids:
                record.quantity_moved += move.product_uom_qty
                record.quantity_remaining = record.quantity - (record.quantity_moved + record.quantity_po)
                if record.quantity_remaining < 0:
                    raise UserError(_("Quantity Remaining cannot be minus!"))

    def _get_vendor_pricelist(self, product):
        """ Function to get vendor pricelist """
        partner_id = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id)])[0]
        return partner_id

    def action_create_rfq(self):
        """ Function to create the purchases related to this request """
        #order lines, copy dari details product request
        for line in self.detail_ids:
            partner_id = self._get_vendor_pricelist(line.product_id)
            order_line = [(0,0,{
                'product_id'  : line.product_id.id,
                'name'        : line.product_id.name,
                'product_qty' : line.quantity,
                'price_unit'  : partner_id.price or line.product_id.standard_price,
            })]
        # create record PO (rfq)
        purchase = self.env['purchase.order'].create({
            'partner_id' : partner_id.name.id, #field id / PK
            'date_order' : fields.Datetime.now(),
            'origin': self.name,
            'order_line': order_line,
            'product_request_id': self.id,
        })
        # update the qty purchased
        for record in self.detail_ids:
            order_ids = self.env['purchase.order.line'].search([
                ('product_id', '=', record.product_id.id),
                ('order_id', '=', purchase.id),
            ])
            for line in order_ids:
                record.quantity_po += line.product_qty
                record.quantity_remaining = record.quantity - (record.quantity_moved + record.quantity_po)
                if record.quantity_remaining < 0:
                    raise UserError(_("Quantity Remaining cannot be minus!"))

    transfer_count = fields.Integer( string="Transfer count", compute="_get_transfer_count")
    po_count = fields.Integer( string="PO count", compute="_get_po_count")

    def _get_transfer_count(self):
        """ Function to count pickings related to this request """
        for record in self:
            record.transfer_count = len(self.transfer_ids)

    def action_view_transfer(self):
        """ Function to view the purchases related to this request """
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        pickings = self.mapped('transfer_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)] # filter supaya hanya picking yg id nya berada di transfer_ids product_request
        elif pickings: # ==1 
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action

    def _get_po_count(self):
        """ Function to count purchases related to this request """
        for record in self:
            record.po_count = len(self.po_ids)

    def action_view_po(self):
        """ Function to view the purchases related to this request """
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        pos = self.mapped('po_ids')
        if len(pos) > 1:
            action['domain'] = [('id', 'in', pos.ids)] # filter supaya hanya po yg id nya berada di po_ids product_request
        elif pos: # ==1 
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = pos.id
        return action
