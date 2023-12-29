# -*- coding: utf-8 -*-
{
    'name': "Ideatime Purchase",

    'summary': """
        Purchase Module for Ideatime""",

    'description': """
        Long description of module's purpose
    """,

    'author': "BEE Data Myanmar",
    'website': "http://www.beedatamyanmar.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'ideatime_budget'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',

        'reports/purchase_order.xml',
        'reports/request_for_quotation.xml',

        'wizard/purchase_detail_report_wizard.xml',
        'wizard/purchase_history_report_wizard.xml',

    ]
}
