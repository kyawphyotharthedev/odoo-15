# -*- coding: utf-8 -*-
{
    'name': "Ideatime HR",

    'summary': """
        Idea Time""",

    'description': """
        Idea Time
            - Model inheritance
            - View inheritance
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '15.0.1',
    'license': 'LGPL-3',

    'depends': ['base', 'hr'],

    'data': [
        'views/personal_data_inherit.xml',

        'security/ir.model.access.csv',
    ],
}