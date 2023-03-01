#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class request_detail(models.Model):
    _name = "vit.request_detail"
    _inherit = "vit.request_detail"
