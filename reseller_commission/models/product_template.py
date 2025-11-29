from odoo import fields , api , models



class ProductTemplate(models.Model) :
    _inherit = 'product.template'


    commision_rate = fields.Float(
        string="Commission %",
        help="Commission percentage for this product. Overrides reseller default rate."
    )