from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError

'''
Traditional Inheritance (Extension Example)
this will not create a table 
just inherit another model to use his attributes or methods
or add functionality to them
'''

class SaleOrder(models.Model) :
    _inherit = 'sale.order'

    property_id = fields.Many2one('property')


    def action_confirm(self):
        res = super().action_confirm()
        print('inside action confirm')
        return res
