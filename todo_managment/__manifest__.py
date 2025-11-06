{
    'name': 'To-Do',
    'version': '1.0',
    'author': 'Ibrahim Ali',
    'category': 'Productivity',
    'depends': ['base' , 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/todo_task_view.xml',
        'wizard/assign_tasks_to_emp_wizard_view.xml',
        'reports/todo_report.xml',
    ],
    'application': True,
    'installable': True,
}
