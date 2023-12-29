# -*- coding: utf-8 -*-
{
    'name': "Ideatime Stock",

    'summary': """
        Stock Module for Ideatime""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'ideatime_core'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_views.xml',
        'views/mrp_production_views.xml',

        'reports/goods_issue_form.xml',
        'reports/goods_received_form.xml',

    ]
}
