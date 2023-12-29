# -*- coding: utf-8 -*-
{
    'name': "Ideatime Core",

    'summary': """
        Ideatime Core""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'uom',
                'mail',
                'product',
                'sale',
                'sale_management',
                'stock',
                'hr',
                'project',
                'calendar',
                'survey',
                'l10n_generic_coa',
                'report_xlsx',
                'base_accounting_kit',
                ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/customer_region.xml',
        'views/item_code_identify.xml',
        'views/product_template.xml',
        'views/res_users_view.xml',
        'views/sale_order_view.xml',
        'views/calendar_view.xml',
        'views/expense_voucher_views.xml',
        'views/uom_uom_views.xml',
        'views/ideatime_project_info_views.xml',
        'views/material_identity_views.xml',
        'views/item_menu_views.xml',
        'views/jo_acceptance_views.xml',
        'views/mail_activity_views.xml',
        'views/product_attribute_views.xml',
        'views/project_contact_particular_views.xml',
        'views/task_survey_views.xml',
        'views/sale_item_category.xml',
        'views/shop_list.xml',

        # 'data/ir_sequence.xml',
        # 'data/hr.xml',
        'data/cost_option.xml',
        'data/project_data.xml',
        'data/res_users.xml',
        'data/ir_rule.xml',

        'reports/project_cost_estimate_parta_layout.xml',
        'reports/project_cost_estimate_partb_layout.xml',
        'reports/decoration_site_survey_form.xml',
        'reports/goods_issue_external_layout.xml',
        'reports/item_description.xml',
        'reports/sale_item_report.xml',

        'wizard/material_item_wizard.xml',
        'wizard/sale_item_wizard.xml',

    ],
}
