#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class po(models.Model):

    _name = "purchase.order"
    _description = "purchase.order"

    _inherit = "purchase.order"


    product_request_id = fields.Many2one(comodel_name="vit.product_request",  string="Product request",  help="", )
