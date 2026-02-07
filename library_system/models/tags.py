import datetime
from email.policy import default

from odoo import models , fields



class Author(models.Model) :
    _name = 'lib.tags'
    _description = 'Book Tags Model For Library'


    sequence = fields.Integer()
    name = fields.Char(required=1)



