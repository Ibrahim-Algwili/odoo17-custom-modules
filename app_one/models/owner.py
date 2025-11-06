from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError

# ---- Traditional Inheritance (Full Model Inheritance)

class Owner(models.Model) :
    _name = 'owner'

    name = fields.Char(required=1 , default='New' , size=20)
    phone = fields.Char()
    address = fields.Char()

    # Relational Fields (will added in the DB as foreign key)
    # Relation (O2M)
    property_ids = fields.One2many('property' , 'owner_id')