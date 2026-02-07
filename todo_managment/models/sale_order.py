from odoo import api, fields, models
from odoo.fields import Command






class Sale_Order(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        print(self , vals_list)
        return super(Sale_Order, self).create(vals_list)



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        print(self , vals_list)
        return super(Sale_Order, self).create(vals_list)