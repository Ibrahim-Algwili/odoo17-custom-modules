# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CommunicationCodes(models.Model):
    _name = 'communication.codes'
    _description = 'إدارة شفرات الاتصالات'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # الحقول الأساسية
    name = fields.Char(
        string='الرقم التسلسلي',
        readonly=True,
        copy=False,
        tracking=True,
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='الموظف',
        tracking=True,
        required=True,
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='الوظيفة',
        related='employee_id.job_id',
        store=True,
        readonly=True,
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='الشركة',
        related='employee_id.company_id',
        store=True,
        readonly=True,
    )
    
    branch_id = fields.Many2one(
        'hr.department',
        string='الفرع',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    
    city = fields.Char(
        string='المدينة',
        tracking=True,
    )
    
    code_number = fields.Char(
        string='رقم الشفرة',
        tracking=True,
        required=True,
    )
    
    code_system = fields.Selection(
        [
            ('prepaid', 'دفع مسبق'),
            ('monthly_invoice', 'فاتورة شهرية'),
            ('other', 'أخرى'),
        ],
        string='نظام الشفرة',
        tracking=True,
        required=True,
        default='prepaid',
    )
    
    monthly_balance = fields.Float(
        string='الرصيد الشهري',
        tracking=True,
    )
    
    code_status = fields.Selection(
        [
            ('in_stock', 'في المخزن'),
            ('delivered', 'تم التسليم'),
            ('suspended', 'موقوفة'),
            ('cancelled', 'ملغاة'),
        ],
        string='حالة الشفرة',
        tracking=True,
        required=True,
        default='in_stock',
    )
    
    code_version = fields.Selection(
        [
            ('original', 'الأصلي'),
            ('new_version', 'إصدار شفرة جديد'),
        ],
        string='إصدار الشفرة',
        tracking=True,
        default='original',
    )
    
    version_note = fields.Text(
        string='ملاحظة الإصدار',
        tracking=True,
    )
    
    delivery_date = fields.Datetime(
        string='تاريخ التسليم',
        tracking=True,
    )
    
    delivery_user_id = fields.Many2one(
        'res.users',
        string='سلمها',
        tracking=True,
    )
    
    notes = fields.Text(
        string='ملاحظات',
        tracking=True,
    )
    
    active = fields.Boolean(
        string='نشط',
        default=True,
        tracking=True,
    )
    
    # SQL Constraint لمنع تكرار رقم الشفرة
    _sql_constraints = [
        ('unique_code_number', 'unique(code_number)', 'رقم الشفرة مستخدم من قبل! يرجى إدخال رقم شفرة مختلف.'),
    ]
    
    # Validation في Python
    @api.constrains('code_number')
    def _check_code_number(self):
        for record in self:
            if not record.code_number:
                raise ValidationError('رقم الشفرة مطلوب!')
            
            # التحقق من تنسيق رقم الشفرة (يمكن تخصيصه حسب الحاجة)
            if len(record.code_number.strip()) < 3:
                raise ValidationError('رقم الشفرة يجب أن يكون على الأقل 3 أحرف!')
            
            # التحقق من تكرار رقم الشفرة في Python
            existing = self.search([
                ('code_number', '=', record.code_number),
                ('id', '!=', record.id),
            ])
            if existing:
                raise ValidationError(f'رقم الشفرة "{record.code_number}" مستخدم بالفعل!')
    
    @api.constrains('monthly_balance')
    def _check_monthly_balance(self):
        for record in self:
            if record.monthly_balance and record.monthly_balance < 0:
                raise ValidationError('الرصيد الشهري لا يمكن أن يكون سالباً!')
    
    # إنشاء رقم تسلسلي تلقائي
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('communication.codes') or 'SIM-0001'
        return super().create(vals_list)
    
    def write(self, vals):
        # عند تغيير رقم الشفرة في أي سجل، يتم تعيين إصدار جديد لذلك السجل
        if 'code_number' in vals:
            for record in self:
                if vals['code_number'] != record.code_number:
                    record.code_version = 'new_version'
        return super().write(vals)
    
    # دالة لإصدار شفرة جديدة للموظف
    def action_create_new_version(self):
        self.ensure_one()
        return {
            'name': 'إصدار شفرة جديدة',
            'type': 'ir.actions.act_window',
            'res_model': 'communication.codes',
            'view_mode': 'form',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_code_version': 'new_version',
                'default_version_note': f'إصدار بديل للشفرة الأصلية: {self.code_number}',
            },
        }
    
    # دالة لتغيير حالة الشفرة
    def action_deliver(self):
        self.ensure_one()
        self.write({
            'code_status': 'delivered',
            'delivery_date': fields.Datetime.now(),
            'delivery_user_id': self.env.user.id,
        })
    
    def action_suspend(self):
        self.ensure_one()
        self.write({'code_status': 'suspended'})
    
    def action_cancel(self):
        self.ensure_one()
        self.write({'code_status': 'cancelled'})
    
    def action_return_to_stock(self):
        self.ensure_one()
        self.write({
            'code_status': 'in_stock',
            'delivery_date': False,
            'delivery_user_id': False,
        })
    
    # دالة لتصدير البيانات
    def action_export_excel(self):
        return {
            'name': 'تصدير إلى Excel',
            'type': 'ir.actions.act_window',
            'res_model': 'export.communication.codes.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_code_ids': [(6, 0, self.ids)]},
        }
    
    # دالة للبحث المتقدم
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args = ['|', ('code_number', operator, name), ('employee_id.name', operator, name)] + args
        return self.search(args, limit=limit).name_get()
