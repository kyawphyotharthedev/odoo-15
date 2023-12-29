# -*- coding: utf-8 -*-
{
    'name': "ideatime_expense",

    'summary': """
        Ideatime Expense""",

    'description': """
        Ideatime Expense
    """,

    'author': "BEE Data Myanmar",
    'website': "http://www.beedatamyanmar.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['ideatime_budget', 'hr_expense'],
    'license': 'LGPL-3',
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/budget_expense_overview_report_data.xml',
        'views/hr_expense_views.xml',
        'views/report_budget_expense_overview.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ideatime_expense/static/src/js/budget_expense_overview_report_backend.js',
        ],
        'web.assets_common': [
            'ideatime_expense/static/src/scss/budget_expense_overview_report.scss',
        ],
    },
    # only loaded in demonstration mode
    'demo': [

    ],
}
