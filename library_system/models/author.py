import datetime
from email.policy import default

from odoo import models , fields



class Author(models.Model) :
    _name = 'author'
    _description = 'Book Author Model For LMS'


    name = fields.Char(required=1)
    birth_date = fields.Date(string="Birth Date")
    image = fields.Image()

    book_ids = fields.One2many('product.template' , 'author_id')


