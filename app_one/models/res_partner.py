from email.policy import default

from odoo import models , fields , api
from odoo.exceptions import ValidationError


class ResPartner(models.Model) :
    _inherit = 'res.partner'

    property_id = fields.Many2one('property')
    price = fields.Float(related="property_id.selling_price")

    # --- Another Way ----
    # price = fields.Float(compute='_compute_price' , store=1)
    #
    # @api.depends('property_id')
    # def _compute_price (self) :
    #     for rec in self :
    #         rec.price = rec.property_id.selling_price


    @api.model_create_multi
    def create(self, vals_list):
        print("env ", self.env)
        print("env.user ", self.env.user)
        print("env.uid ", self.env.uid)
        print("env.is_admin() ", self.env.is_admin())
        print("env.is_superuser() ", self.env.is_superuser())
        print("env.is_system() ", self.env.is_system())
        print("env.context ", self.env.context)
        print("_context ", self._context)
        print("env.cr ", self.env.cr)
        print("env.company ", self.env.company)
        print("env.companies ", self.env.companies)



        return super(ResPartner, self).create(vals_list)