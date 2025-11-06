from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError

'''
Traditional Inheritance (Extension Example)
this will not create a table 
just inherit another model to use his attributes or methods
or add functionality to them
'''

class AccountMove(models.Model) :
    _inherit = 'account.move'

    def action_do_something(self):
        print(self , 'inside action_do_something Method')
