from odoo import models


class Employee(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('user_uniq', 'unique (user_id)', "User already attached !"),
    ]
