import datetime
from email.policy import default

from odoo import models , fields , api


class PropertyOffer (models.Model) :
    _name = "property.offer"


    price = fields.Float()
    status = fields.Selection ([
        ('accepted' , 'Accepted'),
        ('refused' , 'Refused'),
    ] , copy="0" , default=None , readonly=1)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline")
    # Relations
    partner_id = fields.Many2one('res.partner' , required=1)
    property_id = fields.Many2one('property' , required=1)


    @api.depends('validity' , 'create_date')
    def _compute_date_deadline(self) :
        for rec in self :
            rec.date_deadline = rec.create_date + datetime.timedelta(days=rec.validity)

    # Offer Actions
    def action_accept(self):
        for rec in self:
            rec.status = 'accepted'

    def action_refuse(self):
        for rec in self:
            rec.status = 'refused'