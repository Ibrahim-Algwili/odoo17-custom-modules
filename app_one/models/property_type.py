from odoo import models,fields


class PropertyType(models.Model):
    _name = 'property.type'

    name = fields.Char(required=1)
    property_ids = fields.One2many('property' , 'property_type_id')