#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class stock_location(models.Model):

    _name = "stock.location"
    _description = "stock.location"

    _inherit = "stock.location"


