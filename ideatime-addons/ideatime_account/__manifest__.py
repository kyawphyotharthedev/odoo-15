# -*- coding: utf-8 -*-
{
    'name': "Ideatime Account",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

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
    'depends': [
        'base',
        'account',
        'uom',
        'ideatime_core',
        'account_dynamic_reports',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/accounting_menu.xml',
        'views/account_move_view.xml',
        'views/account_bank_statement_views.xml',
        'views/account_payment_view.xml',

        'wizard/account_payment_register_view.xml',
        'reports/beten_invoice_report.xml',
        'reports/invoice_report.xml',
    ],
    'assets': {
    'account_dynamic_reports.assets': [
            ('after', 'account_dynamic_reports/static/src/scss/dynamic_common_style.scss', 'ideatime_account/static/src/scss/style.scss'),
        ],
        'web.assets_backend': [
            'ideatime_account/static/src/js/script.js',
        ],
        'web.assets_qweb': [
            'ideatime_account/static/src/xml/view.xml',
        ]
    },
}
