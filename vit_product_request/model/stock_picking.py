from odoo import models, fields


class StockPicking(models.Model):
    _description = "stock.picking"
    _inherit = "stock.picking"

    product_request_id = fields.Many2one(comodel_name="vit.product_request", string="Product request", help="Related Product Request")
