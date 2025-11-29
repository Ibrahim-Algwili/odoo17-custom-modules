from odoo import models, api, fields
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self, is_modify=False, **kwargs):
        res = super().reverse_moves()

        refund_id = res.get('res_id')
        if not refund_id:
            return res

        refunds = self.env['account.move'].browse(refund_id)

        for refund in refunds:

            # نتحقق أنه Refund
            if refund.move_type != 'out_refund':
                continue

            original = refund.reversed_entry_id
            if not original:
                continue

            # نبحث عن كل خطوط العمولة المرتبطة بهذه الفاتورة
            settlement_lines = self.env['commission.settlement.line'].search([
                ('invoice_id', '=', original.id)
            ])

            if not settlement_lines:
                continue

            # كل هذه الخطوط تعود إلى تسوية واحدة — نأخذها
            settlement = settlement_lines[0].settlement_id

            # نجمع قيمة العمولة المستردة
            total_reclaim = 0.0

            for line in settlement_lines:
                inv = line.invoice_id
                if inv.amount_total == 0:
                    continue

                refund_ratio = abs(refund.amount_total) / inv.amount_total
                reclaim_amount = line.invoice_commission * refund_ratio

                total_reclaim += reclaim_amount

            if total_reclaim <= 0:
                continue

            # احصل على حساب مصروف العمولة (اضبطه حسب نظامك)
            # expense_account = self.env.company.account_expense_id
            # if not expense_account:
            #     raise UserError("Please configure a Commission Expense Account.")


            # إنشاء Vendor Bill
            bill_vals = {
                'move_type': 'in_refund',  # Vendor Credit Note (Correct)
                'partner_id': settlement.reseller_id.id,
                'invoice_origin': original.name,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': [(0, 0, {
                    'name': f'Reclaim commission for refund of {original.name}',
                    'quantity': 1,
                    'price_unit': total_reclaim,
                    # 'account_id': expense_account.id,
                })],
            }

            bill = self.env['account.move'].create(bill_vals)
            bill.action_post()

            # تحديث التسوية
            settlement.reclaim_bill_id = bill.id
            settlement.total_commission -= total_reclaim
            settlement.state = 'reclaimed'


        return res