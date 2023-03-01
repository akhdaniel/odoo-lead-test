#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class transfer(models.Model):

    _name = "stock.picking"
    _description = "stock.picking"

    _inherit = "stock.picking"


    product_request_id = fields.Many2one(comodel_name="vit.product_request",  string="Product request",  help="", )
