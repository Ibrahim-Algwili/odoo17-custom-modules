from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reseller_id = fields.Many2one(
        'res.partner',
        string="Reseller",
        domain=[('is_reseller', '=', True)],
        help="Select the reseller associated with this sale."
    )

    commission_tot = fields.Float(
        string="Reseller Total Commission",
        compute="_compute_commission_total",
        store=True
    )

    @api.depends('order_line.comision_amount')
    def _compute_commission_total(self):
        for order in self:
            order.commission_tot = sum(order.order_line.mapped('comision_amount'))

    def _create_invoices(self, grouped=False, final=False):
        ''' To Get The Reseller From the SO And Throw it To the Invoice in account.move Model '''
        moves = super()._create_invoices(grouped=grouped, final=final)

        for move in moves:
            # get sale.order from invoice line links
            sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')

            if sale_orders:
                # In grouped invoices, there may be multiple orders.
                # Assign reseller only if the reseller is the same across all.
                unique_resellers = sale_orders.mapped('reseller_id')

                if len(unique_resellers) == 1 and unique_resellers[0]:
                    move.reseller_id = unique_resellers[0].id

        return moves

