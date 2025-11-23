from odoo import models , fields ,api


class HospitalPatient(models.Model) :
    _name = 'hospital.patient'
    _description = 'Patient Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string="Name" , required=1 , tracking=1)
    date_of_birth = fields.Date(string="DOB")
    gender = fields.Selection([
        ('male' , 'Male'),
        ('female' , 'Female'),
    ])