{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Manage library books, borrowing, members, inventory, and sales',
    'sequence': 10,
    'description': """Full Library Management System integrated with products, sales, purchase, and inventory.""",
    'category': 'Services/Library',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'depends': ['base', 'product', 'stock', 'sale', 'purchase', 'mail'],
    'data': [
        # Security
        'security/category.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data Files
        'data/sequence.xml',
        'data/server_actioins.xml',
        'data/automated_actions.xml',

        # Views
        'views/product_book_views.xml',
        'views/author_views.xml',
        'views/tags_views.xml',
        'views/library_loan_views.xml',
        'views/menus.xml',
        'views/res_partner_views.xml',

        # Wizards
        'wizard/suggestion_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
