from pytz import common_timezones_set

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commision_rate = fields.Float(
        string="Commision %",
        related="product_id.commision_rate",
        store=1
    )

    comision_amount = fields.Float(
        string="Commision Amount",
        compute="_compute_comision_amount",
    )

    @api.depends('commision_rate' , 'price_subtotal')
    def _compute_comision_amount (self):
        for line in self :
            rate = line.commision_rate
            line.comision_amount = (line.price_subtotal * rate) / 100