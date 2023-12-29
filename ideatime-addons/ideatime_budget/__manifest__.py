# -*- coding: utf-8 -*-
{
    'name': "Ideatime Budget and Expense",

    'summary': """
        Ideatime Budget and Expense""",

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
        'ideatime_account',
        'ideatime_product_configurator',
        'ideatime_stock',
        'report_xlsx',
    ],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'data/budget_overview_report_data.xml',
        'security/ir.model.access.csv',
        'security/permission.xml',
        'views/budget_approval_view.xml',
        'views/budget_template_view.xml',
        'views/stock_picking_view.xml',
        'views/account_payment_view.xml',
        'reports/report_budget_overview.xml',
        'reports/self_purchase_inform_form.xml',
        'reports/delivery_inform_form.xml',
        'reports/project_cost_estimate_analysis.xml',
        'reports/budget_procurement_purchase_form.xml',
        'reports/budget_report.xml',
        'reports/beten_budget_report.xml',
        'reports/pec_overview_report.xml',


    ],
    'assets': {
        'web.assets_backend': [
            'ideatime_budget/static/src/js/budget_overview_report_backend.js',
            'ideatime_budget/static/src/js/pec_overview_report_backend.js',
        ],
        'web.assets_common': [
            'ideatime_budget/static/src/scss/budget_overview_report.scss',
        ],
    }
}
