# -*- coding: utf-8 -*-
{
    'name': "Ideatime Sale",

    'summary': """
        Sale Customization for Ideatime""",

    'description': """
        Long description of module's purpose
    """,

    'author': "BEE Data Myanmar",
    'website': "http://www.beedatamyanmar.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'sale_stock',
        'ideatime_core',
        'project',
        'stock',
        'account',
        'ideatime_product_configurator',
        'partner_base_report',
        'report_xlsx',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',

        'reports/sale_item_information.xml',
        'reports/ideatime_quotation_template.xml',

        'reports/order_agreement_header_layout.xml',
        'reports/order_agreement_report.xml',
        # 'reports/project_cost_estimate_parta.xml',
        # 'reports/project_cost_estimate_partb.xml',
        # 'reports/project_estimate_budget_form.xml',
        # 'reports/project_cost_estimate_analysis.xml',
        'reports/quotation_header_layout.xml',
        # 'reports/project_budget_applicable_plan.xml',
        'reports/project_job_order.xml',
        'reports/samsung_quotation_template.xml',
        'reports/beten_quotation_header_layout.xml',
        'reports/beten_quotation_template.xml',

    ],
}
