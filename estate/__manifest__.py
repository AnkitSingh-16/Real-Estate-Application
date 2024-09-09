{
    'name': "Real Estate",
    # 'version': '1.0',
    'category': 'Real Estate/Brokerage',
    'depends': ['base', 'mail', 'website'],
    'license': 'LGPL-3',
    'data':[
        'security/ir.model.access.csv',
        'security/security.xml',
        "data/master_data.xml",
        'wizard/add_offer_views.xml',
        'views/estate_property_views.xml',
        'views/property_offer_views.xml',
        'views/property_type_views.xml',
        'views/property_tag_views.xml',
        'views/res_users_views.xml',
        'views/properties_template.xml',
        'views/estate_menus.xml',
        'reports/estate_property_reports.xml',
        'reports/estate_property_templates.xml',
    ],
    'demo': [
        'demo/estate_property_demodata.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
