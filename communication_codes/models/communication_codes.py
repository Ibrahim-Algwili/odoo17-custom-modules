# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


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
        copy=False,
        default="091-000-0000"
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
    
    notes = fields.Html(
        string='ملاحظات',
    )
    
    active = fields.Boolean(
        string='نشط',
        default=True,
        tracking=True,
    )
    
    # SQL Constraint لمنع تكرار رقم الشفرة
    _sql_constraints = [
        ('unique_code_number', 'unique(code_number)', 'رقم الشفرة مستخدم من قبل، يرجى إدخال رقم شفرة مختلف.'),
    ]


    def copy(self, default=None):
        '''
        Giving Default Number if Duplicating Record
        Notify The User To Change This Default Number
        '''
        self.ensure_one()
        default = dict(default or {})
        user = self.env.user

        if 'code_number' not in default :
            default['code_number'] = "091-000-0000"

        default.update({
            'code_status': 'in_stock',
            'delivery_date': False,
            'delivery_user_id': False,
        })

        # Giving Notification Message to Change The Number
        message = "قم بتغيير رقم الهاتف"

        self.env['bus.bus']._sendone(
            user.partner_id,
            'simple_notification',
            {
                'title': "تنبيه",
                'message': message,
                'type': 'warning',
                'sticky': False,
            }
        )

        return super().copy(default)
    
    # Validation في Python
    @api.constrains('code_number')
    def _check_code_number(self):
        for record in self:
            if not record.code_number:
                raise ValidationError('رقم الشفرة مطلوب.')
            
            # التحقق من تنسيق رقم الشفرة
            if len(record.code_number.strip()) != 12:
                raise ValidationError(
                    'رقم الشفرة يجب أن يكون 10 أرقام بينها (-) مثل \n'
                    '(091-XXX-XXXX).'
                )
            
            # التحقق من تكرار رقم الشفرة في Python
            existing = self.search([
                ('code_number', '=', record.code_number),
                ('id', '!=', record.id),
            ])
            if existing:
                raise ValidationError(f'رقم الشفرة "{record.code_number}" مستخدم بالفعل.')
    
    @api.constrains('monthly_balance')
    def _check_monthly_balance(self):
        for record in self:
            if record.monthly_balance and record.monthly_balance < 0:
                raise ValidationError('الرصيد الشهري لا يمكن أن يكون سالباً.')
    
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

    def action_current_employee_all_numbers(self):
        self.ensure_one()
        return {
            'name': "كل الأرقام للموظف الحالي",
            'type': "ir.actions.act_window",
            'res_model': "communication.codes",
            'view_mode': "tree,form",
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'create': False},
            'target': "current",
        }
    
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
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name :
            name_domain = ['|', ('code_number', operator, name), ('employee_id.name', operator, name)]
            domain = expression.AND([name_domain, domain])

        return self._search(domain, limit=limit, order=order)

    @api.model
    def get_dashboard_stats(self):
        """Returns enhanced statistics for the dashboard."""
        # تأكد من جلب البيانات للشركات المسموح بها للمستخدم الحالي
        domain = [('company_id', 'in', self.env.companies.ids)]

        # 1. إحصائيات الحالات (Status Counts)
        status_data = self.read_group(domain, ['code_status'], ['code_status'])
        status_counts = {'in_stock': 0, 'delivered': 0, 'suspended': 0, 'cancelled': 0}
        total_count = 0
        for data in status_data:
            val = data.get('code_status_count') or data.get('__count', 0)
            status = data.get('code_status')
            if status in status_counts:
                status_counts[status] = val
                total_count += val

        # 2. إحصائيات الأنظمة (System Counts)
        system_data = self.read_group(domain, ['code_system'], ['code_system'])
        system_counts = {'prepaid': 0, 'monthly_invoice': 0, 'other': 0}
        for data in system_data:
            val = data.get('code_system_count') or data.get('__count', 0)
            system = data.get('code_system')
            if system in system_counts:
                system_counts[system] = val

        # 3. إجمالي الرصيد وعدد الشركات
        balance_data = self.read_group(domain, ['monthly_balance:sum'], [])
        total_balance = balance_data[0].get('monthly_balance') or 0

        # حساب عدد الشركات الفريدة التي لديها سجلات
        company_count = self.env['communication.codes'].search_count(domain)  # أو يمكنك جلبها من read_group للشركات

        # 4. إحصائيات الشركات (للجدول والـ Progress Bars)
        company_group = self.read_group(domain, ['company_id'], ['company_id'], limit=5,
                                        orderby='company_id_count desc')
        company_stats = []
        for comp in company_group:
            count = comp.get('company_id_count') or comp.get('__count', 0)
            company_stats.append({
                'name': comp.get('company_id')[1] if comp.get('company_id') else _('Unknown'),
                'count': count,
                'percent': (count / total_count * 100) if total_count > 0 else 0
            })

        # 5. أحدث 5 سجلات مضافة (للجدول الجانبي)
        recent_records = self.search(domain, limit=5, order='create_date desc')
        recent_codes = []

        # خريطة الألوان للحالات لتناسب التنسيق الجديد
        color_map = {
            'in_stock': 'success',
            'delivered': 'info',
            'suspended': 'warning',
            'cancelled': 'danger'
        }

        # جلب أسماء الحالات المترجمة
        status_selection = dict(self._fields['code_status'].selection)

        for rec in recent_records:
            recent_codes.append({
                'id': rec.id,
                'code_number': rec.code_number or rec.name,
                'employee_name': rec.employee_id.name or _('No Employee'),
                'status_name': status_selection.get(rec.code_status, ''),
                'status_color': color_map.get(rec.code_status, 'secondary'),
            })

        return {
            'total_count': total_count,
            'status_counts': status_counts,
            'system_counts': system_counts,
            'total_balance': total_balance,
            'company_count': len(company_group),
            'company_stats': company_stats,
            'recent_codes': recent_codes,
        }