from odoo import models, fields, api, _
from odoo.exceptions import UserError


STATES = [('draft', 'Draft'), ('open', 'Open'), ('done','Done')]

class ProductRequest(models.Model):
    _name = "vit.product_request"
    _description = "vit.product_request"

    name = fields.Char( required=True, default="New", readonly=True, string="Name", help="nomor dokumen request")
    date = fields.Date( string="Date", readonly=True, states={"draft" : [("readonly",False)]}, help="input transaction date")
    date_required = fields.Date( string="Date required", readonly=True, states={"draft" : [("readonly",False)]}, help="input required date")
    reason = fields.Html( string="Reason", readonly=True, states={"draft" : [("readonly",False)]}, help="reason in HTML")
    state = fields.Selection(selection=STATES, readonly=True, default=STATES[0][0], string="State", help="State of the request")
    transfer_count = fields.Integer( string="Transfer count", readonly=True, states={"draft" : [("readonly",False)]}, help="Transfer related to the request")
    po_count = fields.Integer( string="Po count", readonly=True, states={"draft" : [("readonly",False)]}, help="Purchases related to the request", )

    @api.model
    def create(self, vals):
        """ Override the create button to add the name based on the sequence """
        if not vals.get("name", False) or vals["name"] == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("vit.product_request") or "Error Number!!!"
        return super(ProductRequest, self).create(vals)

    def action_confirm(self):
        """ Action to set the state to the open """
        self.state = STATES[1][0]

    def action_done(self):
        """ Action to set the state to the done """
        self.state = STATES[2][0]

    def action_draft(self):
        """ Action to set the state to the draft """
        self.state = STATES[0][0]

    def unlink(self):
        """ Override the delete function to constrain delete record that is not on draft """
        for me_id in self :
            if me_id.state != STATES[0][0]:
                raise UserError("Cannot delete non draft record!")
        return super(ProductRequest, self).unlink()

    location_dest_id = fields.Many2one(comodel_name="stock.location", string="Location dest", readonly=True, states={"draft" : [("readonly",False)]}, help="", )
    detail_ids = fields.One2many(comodel_name="vit.request_detail", inverse_name="product_request_id", string="Detail", readonly=True, states={"draft" : [("readonly",False)]}, help="", )
    transfer_ids = fields.One2many(comodel_name="stock.picking", inverse_name="product_request_id", string="Transfer", readonly=True, states={"draft" : [("readonly",False)]}, help="", )
    po_ids = fields.One2many(comodel_name="purchase.order", inverse_name="product_request_id", string="Po", readonly=True, states={"draft" : [("readonly",False)]}, help="", )
