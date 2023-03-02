#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class request_detail(models.Model):
    _name = "vit.request_detail"
    _inherit = "vit.request_detail"

    def _getQtyMoved(self):
        for rec in self :
            done_picking_ids = rec.product_request_id.transfer_ids.filtered(lambda r: r.state=='done')
            rec.quantity_moved = sum(done_picking_ids.move_ids_without_package.filtered(lambda r: r.product_id==rec.product_id).mapped('quantity_done'))
        return True

    def _getQtyPO(self):
        for rec in self :
            po_ids = rec.product_request_id.po_ids.filtered(lambda r: r.state in ["purchase","done"])
            rec.quantity_po = sum(po_ids.order_line.filtered(lambda r: r.product_id==rec.product_id).mapped('product_qty'))
        return True

    def _getRemainingQty(self):
        for rec in self :
            rec.quantity_remaining = rec.quantity - rec.quantity_moved - rec.quantity_po
        return True

    def _getAllowCreateProduct(self):
        for rec in self:
            rec.allow_create_product = True
            if rec.product_id :
                rec.allow_create_product = False
        return True

    quantity_moved = fields.Integer(compute=_getQtyMoved, string="Quantity moved",  help="", )
    quantity_po = fields.Integer(compute=_getQtyPO, string="Quantity po",  help="", )
    quantity_remaining = fields.Integer(compute=_getRemainingQty, string="Quantity remaining",  help="", )
    allow_create_product = fields.Boolean(compute=_getAllowCreateProduct, )

    def create_product(self):
        self.ensure_one()
        if not self.product_id :
            # buat product baru dari description request line
            new_product_id = self.env["product.product"].create({'name': self.name,})
            action = self.env.ref('vit_product_request.action_product').sudo().read()[0]
            action['views'] = [(self.env.ref('product.product_normal_form_view').id, 'form')]
            action['res_id'] = new_product_id.id

            # update product di request line
            self.product_id = new_product_id

            return action