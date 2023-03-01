#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class request_detail(models.Model):

    _name = "vit.request_detail"
    _description = "vit.request_detail"
    name = fields.Char( required=True, string="Name",  help="", )
    spesification = fields.Text( string="Spesification",  help="", )
    brochure = fields.Binary( string="Brochure",  help="", )
    quantity = fields.Integer( string="Quantity",  help="", )
    quantity_moved = fields.Integer( string="Quantity moved",  help="", )
    quantity_po = fields.Integer( string="Quantity po",  help="", )
    quantity_remaining = fields.Integer( string="Quantity remaining",  help="", )


    product_request_id = fields.Many2one(comodel_name="vit.product_request",  string="Product request",  help="", )
    product_id = fields.Many2one(comodel_name="product.product",  string="Product",  help="", )
