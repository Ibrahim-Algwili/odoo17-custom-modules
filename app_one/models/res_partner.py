from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError


class ResPartner(models.Model) :
    _inherit = 'res.partner'

    property_id = fields.Many2one('property')
    price = fields.Float(related="property_id.selling_price")

    # --- Another Way ----
    # price = fields.Float(compute='_compute_price' , store=1)
    #
    # @api.depends('property_id')
    # def _compute_price (self) :
    #     for rec in self :
    #         rec.price = rec.property_id.selling_price

