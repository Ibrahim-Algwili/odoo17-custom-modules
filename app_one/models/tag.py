from odoo import models , fields


class Tag(models.Model) :
    _name = "tag"

    name = fields.Char(required=1)

    _sql_constraints = [
        ('Unique_Name' , 'unique(name)' , 'This Name is Exist')
    ]