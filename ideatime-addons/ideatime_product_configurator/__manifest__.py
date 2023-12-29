# -*- coding: utf-8 -*-
{
    'name': "Ideatime Product Configurator",

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
    'depends': ['base', 'web', 'product', 'sale', 'ideatime_core', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_configurator_view.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ideatime_product_configurator/static/src/js/configure_section_and_note.js',
            'ideatime_product_configurator/static/src/js/product_configurator_controller.js',
            'ideatime_product_configurator/static/src/js/product_configurator_mixin.js',
            'ideatime_product_configurator/static/src/js/product_configurator_renderer.js',
            'ideatime_product_configurator/static/src/js/product_configurator_view.js',
            'ideatime_product_configurator/static/src/scss/product_configurator.scss',
        ]
    }
}
