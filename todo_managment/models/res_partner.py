from odoo import models , fields




class Res_Partner(models.Model):
    _inherit = 'res.partner'

    to_do_ids = fields.One2many('todo.task' , 'partner_id')
