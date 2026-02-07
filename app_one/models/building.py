from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute


class Building(models.Model) :
    _name = 'building'
    _description = 'Building Record'
    _inherit = ['mail.thread' , 'mail.activity.mixin']
    _rec_name = 'code'


    no = fields.Integer()
    code = fields.Char()
    description = fields.Text()
    active = fields.Boolean() # this used for Archiving