{
    'name': 'Reseller Commission Management',
    'version': '1.0',
    'depends': ['base', 'product', 'stock', 'sale', 'purchase', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/commission_settlement_views.xml',
        'views/sale_order_views.xml',
        'views/menu.xml',
        'report/commission_report.xml',
    ],
    'application' : True ,
}
