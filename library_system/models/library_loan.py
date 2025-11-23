from odoo import models, fields, api
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class LibraryLoan(models.Model):
    _name = "library.loan"
    _description = "Library Loan"
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']

    borrower_id = fields.Many2one("res.partner", string="Borrower", required=True)
    ref = fields.Char(default='New', readonly=True)
    loan_date = fields.Date(string="Loan Date", default=fields.Date.today, tracking=1)
    expected_return = fields.Date(string="Expected Return Date", tracking=1)
    actual_return = fields.Date(string="Actual Return Date")
    state = fields.Selection([
        ('draft', "Draft"),
        ('loaned', "In-Loan"),
        ('returned', "Returned"),
        ('cancel', "Cancel"),
    ], default="draft", tracking=1)
    loan_line_ids = fields.One2many("library.loan.line", "loan_id", string="Books")
    active = fields.Boolean(default=True)
    is_overdue = fields.Boolean(compute="_compute_is_overdue", store=True)

    @api.depends("expected_return", "state")
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_overdue = rec.expected_return and rec.expected_return < today and rec.state == "loaned"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.ref == 'New':
                rec.ref = self.env['ir.sequence'].next_by_code('loan_seq')
        return records

    # -------------------------
    # Confirm Loan
    # -------------------------
    def _remove_books_from_stock(self, loan):
        """Remove the books quantity from LWHBS/Stock location"""
        StockLocation = self.env['stock.location']
        stock_loc = StockLocation.search([
            ('name', '=', 'Stock'),
            ('warehouse_id.code', '=', 'LWHBS'),
            ('usage', '=', 'internal')
        ], limit=1)
        if not stock_loc:
            raise UserError("Stock location LWHBS/Stock not found.")

        for line in loan.loan_line_ids:
            product = line.product_id
            qty_to_remove = float(line.quantity or 0.0)

            # Get stock quants for this location
            quants = product.stock_quant_ids.filtered(lambda q: q.location_id == stock_loc)
            total_qty = sum(quants.mapped('quantity'))

            if total_qty < qty_to_remove:
                raise UserError(
                    f"Not enough quantity for '{product.name}' in {stock_loc.display_name}."
                )

            # Remove quantity directly from quants
            for quant in quants:
                if quant.quantity >= qty_to_remove:
                    quant.quantity -= qty_to_remove
                    qty_to_remove = 0
                    break
                else:
                    qty_to_remove -= quant.quantity
                    quant.quantity = 0

    def action_confirm(self):
        for loan in self:
            if not loan.loan_line_ids:
                raise UserError("You must add at least one book.")

            # Check overdue loans
            overdue = self.env['library.loan'].search([
                ('borrower_id', '=', loan.borrower_id.id),
                ('state', '=', 'loaned'),
                ('expected_return', '<', fields.Date.today())
            ])
            if overdue:
                raise UserError("Can't borrow while you have overdue loans")

            # Check max allowed books per membership type
            borrower = loan.borrower_id
            max_allowed = borrower.max_books_allowed or 0
            active_loans = self.env['library.loan.line'].search([
                ('loan_id.borrower_id', '=', borrower.id),
                ('loan_id.state', '=', 'loaned')
            ])
            total_current_books = sum(active_loans.mapped('quantity'))
            new_books = sum(loan.loan_line_ids.mapped('quantity'))
            if total_current_books + new_books > max_allowed:
                raise UserError(
                    f"Can't borrow more than {max_allowed} books. "
                    f"Currently borrowed: {total_current_books}, requested: {new_books}"
                )

            # Remove books from stock
            self._remove_books_from_stock(loan)

            # Mark as loaned
            loan.state = "loaned"

    # -------------------------
    # Return Loan
    # -------------------------
    def _return_books_to_stock(self, loan):
        """Return books from a loan back to LWHBS/Stock location"""
        StockLocation = self.env['stock.location']
        stock_loc = StockLocation.search([
            ('name', '=', 'Stock'),
            ('warehouse_id.code', '=', 'LWHBS'),
            ('usage', '=', 'internal')
        ], limit=1)
        if not stock_loc:
            raise UserError("Stock location LWHBS/Stock not found.")

        for line in loan.loan_line_ids:
            product = line.product_id
            qty_to_add = float(line.quantity or 0.0)

            # Add quantity back to the first internal quant
            internal_quants = product.stock_quant_ids.filtered(lambda q: q.location_id == stock_loc)
            if internal_quants:
                internal_quants[0].quantity += qty_to_add
            else:
                # If no quant exists yet, create one
                self.env['stock.quant'].create({
                    'product_id': product.id,
                    'location_id': stock_loc.id,
                    'quantity': qty_to_add,
                })

    def action_return(self):
        for loan in self:
            if loan.state != 'loaned':
                raise UserError("Only loaned books can be returned.")

            # Return books to stock
            self._return_books_to_stock(loan)

            # Update loan state
            loan.state = 'returned'
            loan.actual_return = fields.Date.today()

    # -----------------------------------------------------
    # Cancel Loan
    # -----------------------------------------------------
    def action_cancel(self):
        """Cancel the loan"""
        for loan in self:
            if loan.state == "loaned":
                raise UserError("Cannot cancel a loan that is already loaned. Return it instead.")
            loan.state = "cancel"

    # -----------------------------------------------------
    # Reset to Draft
    # -----------------------------------------------------
    def action_reset_draft(self):
        for loan in self:
            loan.state = "draft"

    def cron_overdue_notification(self):
        today = fields.Date.today()
        overdue_loans = self.search([
            ('state', '=', 'loaned'),
            ('expected_return', '<', today),
        ])
        if not overdue_loans:
            return True

        # إرسال التنبيه للمسؤولين (مثال: admin user)
        admin = self.env.ref('base.user_admin')

        message_lines = []
        for loan in overdue_loans:
            books = ", ".join(loan.loan_line_ids.mapped("product_id.name"))
            borrower = loan.borrower_id.name or "Unknown"
            message_lines.append(f"{borrower} - {books} - due: {loan.expected_return}")

        message_body = "<b>تنبيه: كتب متأخرة للإرجاع:</b><br/>" + "<br/>".join(message_lines)

        # إرسال رسالة مرتبطة بمستخدم admin
        self.env['mail.message'].sudo().create({
            'model': 'res.users',
            'res_id': admin.id,
            'body': message_body,
            'subject': "Overdue Loan Alert",
            'message_type': 'notification',  # notification يظهر في Chatter
            'subtype_id': self.env.ref('mail.mt_note').id,
            'author_id': admin.partner_id.id,
        })

        @api.constrains('borrower_id')
        def _check_max_loans(self):
            for loan in self:
                borrower = loan.borrower_id
                max_allowed = borrower.max_books_allowed or 0

                # عدد الكتب التي لديه حالياً في إعارات نشطة
                active_loans = self.env['library.loan.line'].search([
                    ('loan_id.borrower_id', '=', borrower.id),
                    ('loan_id.state', '=', 'loaned')
                ])
                total_current_books = sum(active_loans.mapped('quantity'))

                # عدد الكتب الجديدة في هذه الإعارة
                new_books = sum(loan.loan_line_ids.mapped('quantity'))

                if total_current_books + new_books > max_allowed:
                    raise UserError(
                        f"Can't borrow more than {max_allowed} books. "
                        f"Currently borrowed: {total_current_books}, requested: {new_books}"
                    )


    # ---- Wizard ----
    def action_open_suggestion_wizard(self):
        self.ensure_one()
        return {
            'name': "Book Suggestions",
            'type': 'ir.actions.act_window',
            'res_model': 'suggestion.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_loan_id': self.id,
            },
        }


# ---------------------------------------------------------
# Loan Line (NO LOTS)
# ---------------------------------------------------------
class LibraryLoanLine(models.Model):
    _name = "library.loan.line"
    _description = "Loan Line"

    loan_id = fields.Many2one("library.loan", string="Loan", ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Book", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise UserError('Quantity Should Be Over Zero')

    @api.constrains('loan_id', 'product_id')
    def _check_duplicate_books(self):
        for line in self:
            product_ids = line.loan_id.loan_line_ids.mapped('product_id')
            if product_ids.ids.count(line.product_id.id) > 1:
                raise UserError("Can't Add The same Book in the same Loan Operation")

    @api.constrains('quantity')
    def _lock_quantity_after_confirm(self):
        for line in self:
            if line.loan_id.state != 'draft':
                raise UserError("Can't Change Quantity After Confirm")
