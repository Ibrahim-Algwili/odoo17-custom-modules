from odoo import models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # def _reconcile(self, *args, **kwargs):
    #     # استدعاء الدالة الأصلية لتقوم بعمل reconciliation
    #     res = super()._reconcile(*args, **kwargs)
    #
    #     # بعد المصالحة، تحقق لكل move_line مرتبطة بالـ reconciliation
    #     for line in self:
    #         move = line.move_id
    #         # شرط: الفاتورة customer invoice وليست Vendor Bill أو Credit Note
    #         if move.move_type == 'out_invoice':
    #             # إذا صارت Paid بالكامل
    #             if move.payment_state == 'paid':
    #                 move.commission_ready = True
    #
    #     return res
