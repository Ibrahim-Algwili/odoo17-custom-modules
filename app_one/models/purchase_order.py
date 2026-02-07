from odoo import api, fields, models, exceptions
from odoo import Command


class purchase_order(models.Model):
    _inherit = 'purchase.order'


    @api.model_create_multi
    def create(self, vals_list):
        print(self , vals_list)
        return super(purchase_order, self).create(vals_list)

    def write(self, vals):
        print(self, vals)
        return super().write(vals)



class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        print(self, vals_list)
        return super(purchase_order_line, self).create(vals_list)

    def write(self, vals):
        print(self, vals)
        return super().write(vals)