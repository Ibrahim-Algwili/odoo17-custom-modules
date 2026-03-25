{
    'name': 'Communication Codes Management',
    'name_en': 'Communication Codes Management',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'إدارة شفرات الاتصالات (SIM) للموظفين',
    'description': """
        موديول متكامل لإدارة شفرات الاتصالات (SIM)
        ==========================================
        
        الميزات:
        - إدارة شفرات الموظفين
        - دعم اللغة العربية و RTL
        - استيراد وتصدير Excel
        - تتبع التغييرات
        - إصدار شفرات جديدة
    """,
    'author': 'SIM Management',
    'website': 'https://example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/communication_codes_security.xml',
        'data/communication_codes_data.xml',
        'views/communication_codes_views.xml',
        'views/communication_codes_menu.xml',
        'wizard/import_communication_codes_view.xml',
        'wizard/export_communication_codes_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

