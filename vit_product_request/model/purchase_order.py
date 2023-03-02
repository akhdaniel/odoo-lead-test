from odoo import models, fields


class PurchaseOrder(models.Model):
    _description = "purchase.order"
    _inherit = "purchase.order"

    product_request_id = fields.Many2one(comodel_name="vit.product_request", string="Product request", help="Related Product Request")
