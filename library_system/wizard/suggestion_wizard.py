from odoo import models , fields , api



class SuggestionWizard(models.TransientModel):
    _name = "suggestion.wizard"
    _description = "Suggest Similar Books Wizard"

    loan_id = fields.Many2one("library.loan", string="Loan")
    suggested_book_ids = fields.Many2many("product.product", string="Suggested Books")
    message = fields.Text(string="Why these books?", readonly=True)


    def action_suggest(self):
        """
        This method generates book suggestions based on the tags and authors
        of the books in the selected loan.
        """

        self.ensure_one()  # Ensure we are working on a single wizard record

        # Step 1: Get all books from this loan
        loan_books = self.loan_id.loan_line_ids.mapped('product_id')

        # Step 2: Collect tags and authors of these books
        tags = loan_books.mapped('tag_ids').ids
        authors = loan_books.mapped('author_id').ids

        # Step 3: Search for similar books by matching tags OR authors
        similar_books = self.env['product.product'].search([
            '|',
            ('tag_ids', 'in', tags),
            ('author_id', 'in', authors)
        ], limit=3)  # Limit to 3 suggestions

        # Step 4: Update the wizard fields with the suggested books
        self.suggested_book_ids = [(6, 0, similar_books.ids)]

        # Step 5: Prepare a textual explanation
        tag_names = ", ".join(loan_books.mapped('tag_ids.name'))
        author_names = ", ".join(loan_books.mapped('author_id.name'))
        self.message = f"Suggested based on tags: {tag_names} and authors: {author_names}."

        # Step 6: Return action to keep wizard open and show updated fields
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'suggestion.wizard',
            'view_mode': 'form',
            'res_id': self.id,  # Open the same wizard record
            'target': 'new',  # Open as a popup
        }

