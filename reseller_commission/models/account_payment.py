from email.policy import default

from odoo import models , api , fields



class AccountPayment(models.Model) :
    _inherit = 'account.payment'

