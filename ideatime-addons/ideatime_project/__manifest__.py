# -*- coding: utf-8 -*-
{
    'name': "Ideatime Project",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

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
    'depends': [
        'base',
        'product',
        'sale',
        'project',
        'hr',
        'ideatime_product_configurator',
        'ideatime_core',
        'ideatime_budget',
        'task_check_list',
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/action_step_template_view.xml',
        'views/cost_option_views.xml',
        'views/design_proposal_views.xml',
        'views/idea_income_expense_views.xml',
        'views/initial_feedback_process_views.xml',
        'views/project_project_views.xml',
        'views/project_site_views.xml',
        'views/project_task_type_views.xml',
        'views/project_task_views.xml',
        'views/project_type_views.xml',
        'views/shop_list_views.xml',

        'reports/idea_in_ex_report.xml',
        'reports/budget_report.xml',
        'reports/project_estimate_analysis.xml',

        'wizard/project_report_xlsx_wizard.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'ideatime_project/static/src/js/project_in_ex.js',
        ]
    }
}
