from odoo import models, fields


class request_detail(models.Model):
    _name = "vit.request_detail"
    _description = "vit.request_detail"

    name = fields.Char( required=True, string="Name", help="Name of the request detail")
    spesification = fields.Text( string="Spesification", help="Specification of the request detail")
    brochure = fields.Binary( string="Brochure", help="Brochure of the request detail")
    quantity = fields.Integer( string="Quantity", help="Initial Requested of the Quantity")
    quantity_moved = fields.Integer( string="Quantity moved", help="Fulfilled Quantity from pickings")
    quantity_po = fields.Integer( string="Quantity po", help="Fulfilled Quantity from purchases")
    quantity_remaining = fields.Integer( string="Quantity remaining", help="Remaining Quantity")
    product_request_id = fields.Many2one(comodel_name="vit.product_request", string="Product request", help="Product Request")
    product_id = fields.Many2one(comodel_name="product.product", string="Product", help="Product of the request detail")
