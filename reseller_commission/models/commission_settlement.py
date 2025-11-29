import datetime
from datetime import timedelta
from email.policy import default
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionSettlement(models.Model):
    _name = 'commission.settlement'
    _description = 'Commission Settlement'

    active = fields.Boolean(default=True)
    ref = fields.Char(string="Ref" , default='New')

    reseller_id = fields.Many2one(
        'res.partner',
        string="Reseller",
        required=True,
        domain=[('is_reseller', '=', True)]
    )

    period_from = fields.Date(required=1 , default=datetime.datetime.today() - timedelta(days=5))
    period_to = fields.Date(required=1 , default=datetime.datetime.today())

    settlement_line_ids = fields.One2many(
        'commission.settlement.line',
        'settlement_id',
        string="Commission Lines",
    )

    total_commission = fields.Monetary(
        string="Total Commission",
        compute="_compute_total_commission",
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    reclaim_bill_id = fields.Many2one(
        'account.move',
        string="Reclaim Vendor Bill",
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('accepted', 'Accepted'),
        ('reclaimed', 'Reclaimed'),
    ], default='draft')

    invoice_ids_used = fields.Many2many(
        'account.move',
        compute = '_compute_invoices_used'
    )

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('commission.settlement.sequence') or 'New'

        return res

    @api.depends('settlement_line_ids.invoice_commission')
    def _compute_total_commission(self):
        ''' Computing The Total Commission for the Re-seller '''
        for rec in self:
            rec.total_commission = sum(rec.settlement_line_ids.mapped('invoice_commission'))


    def action_accepted(self):
        '''
        Change the state To Draft ,
        Assign Move in account.move model for the Commission ,
        Validation if There is No Invoice Lines
        '''
        for rec in self:
            if rec.settlement_line_ids:
                rec.state = 'accepted'
                bill_vals = {
                    'move_type' : 'in_invoice' ,      # Vendor Bill
                    'partner_id' : rec.reseller_id.id,
                    'invoice_date' : datetime.datetime.today() ,
                    'currency_id' : rec.currency_id.id ,
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': 'Reseller Commission for invoices: ...',
                            'quantity': 1,
                            'price_unit': rec.total_commission,
                        })
                    ]
                }

                bill = rec.env['account.move'].create(bill_vals)
                bill.action_post()  # confirms the vendor bill

            else:
                raise ValidationError("You Can't Put the State on Accepted \n You Have no Invoice Lines")

            # Forbid the Accepted Invoices from Invoice lines
            invoices = rec.mapped('settlement_line_ids.invoice_id')
            invoices.write({'is_commission_accepted' : True})


    def action_draft(self):
        ''' Change the state To Draft '''
        for rec in self:
            rec.state = 'draft'
            # Debugging
            # import pdb
            # pdb.set_trace()

    def unlink(self):
        ''' Validation To Forbid Deletion While the state is Draft  '''
        for rec in self:
            if rec.state not in 'draft' :
                raise ValidationError("You Can't Delete in Accepted State")
        super().unlink()


    @api.depends('settlement_line_ids.invoice_id')
    def _compute_invoices_used(self):
        ''' To Forbid Duplication of Invoices '''
        for rec in self:
            rec.invoice_ids_used = rec.settlement_line_ids.mapped('invoice_id')
            _logger.warning('ids used is : ' , rec.invoice_ids_used.ids)

