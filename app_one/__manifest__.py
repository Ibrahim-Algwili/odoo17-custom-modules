{
    'name' : 'Real State',
    'author' : 'Ibrahim Ali',
    'category' : '' ,
    'version' : '17.0.0.1.0',
    'depends' : ['base'  , 'sale'  , 'account' , 'mail' , 'contacts'],
    'data' : [
        'security/category.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/property_view.xml',
        'views/building_view.xml',
        'views/owner_view.xml',
        'views/tag_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/property_history_view.xml',
        'views/account_move_view.xml',
        'wizard/change_state_wizard.xml',
        'reports/property_report.xml',
    ] ,
    'assets' : {
        'web.assets_backend' : ['app_one/static/src/css/property.css']
    } ,
    'application' : True,
    'installable': True,

}