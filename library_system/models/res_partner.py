from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    loan_count = fields.Integer(compute="_compute_loan_count")

    membership_type = fields.Selection([
        ('student', 'Student'),
        ('employee', 'Employee'),
        ('general', 'General'),
    ], string="Membership Type", default='general')

    max_books_allowed = fields.Integer(string="Max Books Allowed", compute="_compute_max_books_allowed" , store=False)

    def _compute_max_books_allowed(self):
        '''
        Number of Books Allowed according to the membership
        '''
        for partner in self:
            if partner.membership_type == 'student':
                partner.max_books_allowed = 7
            elif partner.membership_type == 'employee':
                partner.max_books_allowed = 5
            elif partner.membership_type == 'general':
                partner.max_books_allowed = 2
            else:
                partner.max_books_allowed = 0


    def _compute_loan_count(self):
        for partner in self:
            partner.loan_count = self.env['library.loan'].search_count([
                ('borrower_id', '=', partner.id),
                # ('state', '=', 'loaned')
            ])

    def action_view_loans(self):
        self.ensure_one()
        return {
            'name': 'Loans',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'tree,form',
            'domain': [('borrower_id', '=', self.id)],
            'context': {'default_borrower_id': self.id},
        }
