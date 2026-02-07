from email.policy import default

from odoo import models , api , fields



class AccountMove(models.Model) :
    _inherit = 'account.move'

    reseller_id = fields.Many2one('res.partner', string="Reseller")
    is_commission_accepted= fields.Boolean(default=False)
    commission_ready = fields.Boolean(
        compute="_compute_commission_paid",
        default=False,
        store=True,
        help="This invoice is fully paid and ready to be used in commission settlements."
    )


    @api.depends('payment_state')
    def _compute_commission_paid(self):
        '''
        Make commission_ready = True
        if payment_state is paid
        Benefit : We don't Get any Invoices in Commissions App That is Not Paid
        '''
        for invoice in self:
            invoice.commission_ready = (invoice.state == 'posted' and invoice.payment_state == 'paid')


    def _cron_update_commission_ready(self):
        '''
        Stopped for Now!!!
        Search for paid Invoices
        Make the commission_ready field as True to show them in Commission Module
        '''
        # invoices = self.search([
        #     ('move_type', '=', 'out_invoice'),
        #     ('state', '=', 'posted'),
        #     ('commission_ready', '=', False),
        #     ('payment_state', '=', 'paid')
        # ])
        #
        # invoices.write({'commission_ready': True})




