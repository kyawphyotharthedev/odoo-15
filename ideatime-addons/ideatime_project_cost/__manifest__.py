# -*- coding: utf-8 -*-
{
    'name': "Ideatime Project Cost",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'l10n_generic_coa', 'stock', 'project', 'ideatime_project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/project_cost_journal_generate.xml',

        "views/account_views.xml",
        'views/project_views.xml',
        "views/stock_views.xml",
    ],
    'post_init_hook': '_configure_journals',
}
