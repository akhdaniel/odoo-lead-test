#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class product(models.Model):

    _name = "product.product"
    _description = "product.product"

    _inherit = "product.product"


