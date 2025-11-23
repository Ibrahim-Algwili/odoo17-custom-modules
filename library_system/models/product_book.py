from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_book = fields.Boolean(string="Is a Book")
    isbn = fields.Char(string="ISBN")

    author_id = fields.Many2one('author', string="Author" , required=False)
    tag_ids = fields.Many2many('lib.tags' , string="Tags")

    # is_loaned = fields.Boolean()

    loan_count = fields.Integer(
        string="Loaned Count",
        compute="_compute_loan_count"
    )

    def _compute_loan_count(self):
        Loan = self.env['library.loan']
        for template in self:
            template.loan_count = Loan.search_count([
                ('loan_line_ids.product_id.product_tmpl_id', '=', template.id)
            ])

    def action_view_loans(self):
        self.ensure_one()
        return {
            'name': 'Loanes',
            'type': 'ir.actions.act_window',
            'res_model': 'library.loan',
            'view_mode': 'tree,form',
            'domain': [('loan_line_ids.product_id.product_tmpl_id', '=', self.id)],
            'context': {'default_product_tmpl_id': self.id},
        }