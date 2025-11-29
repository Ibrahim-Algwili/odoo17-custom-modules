from odoo import models, fields, api

class CommissionSettlementLine(models.Model):
    _name = "commission.settlement.line"
    _description = "Commission Settlement Line"
    _order = "invoice_id"

    settlement_id = fields.Many2one(
        'commission.settlement',
        string="Settlement",
        ondelete='cascade'
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice",
        required=True,
        domain=[
            ('move_type', '=', 'out_invoice'),
        ],
    )


    invoice_total = fields.Monetary(
        string="Invoice Total",
        currency_field='currency_id',
        compute="_compute_invoice_amounts",
        store=True,
    )

    invoice_commission = fields.Monetary(
        string="Commission Amount",
        currency_field='currency_id',
        compute="_compute_invoice_amounts",
        store=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )

    is_refunded = fields.Boolean(
        string="Refunded",
        compute="_compute_is_refunded",
        store=True
    )

    # ------- Functions -----------

    @api.depends(
        'invoice_id',
        'invoice_id.reversal_move_id',
        'invoice_id.reversal_move_id.state',
        'invoice_id.reversal_move_id.move_type'
    )
    def _compute_is_refunded(self):
        for rec in self:
            rec.is_refunded = bool(rec.invoice_id.reversal_move_id)


    # The compute method for calculating amounts:
    @api.depends('invoice_id')
    def _compute_invoice_amounts(self):
        for line in self:
            # Check if invoice is linked
            if not line.invoice_id:
                line.invoice_total = 0.0
                line.invoice_commission = 0.0
                continue

            invoice = line.invoice_id

            # 1) Calculate Total Invoice Amount
            line.invoice_total = invoice.amount_total

            # 2) Calculate Commission Amount
            total_commission = 0.0
            for inv_line in invoice.invoice_line_ids:
                product = inv_line.product_id
                # Get commission rate from product (assuming it's defined on product.template)
                rate = product.commision_rate or 0
                subtotal = inv_line.price_subtotal

                total_commission += (subtotal * rate) / 100

            line.invoice_commission = total_commission



