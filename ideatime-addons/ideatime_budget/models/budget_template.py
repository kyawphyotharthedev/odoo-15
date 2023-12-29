# -*- coding: utf-8 -*-

from odoo import models, fields


class BudgetTemplate(models.Model):
    _name = 'budget.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    name = fields.Char(required=True)

    partA = fields.Boolean(string="Project Cost Estimate Part A")
    partB = fields.Boolean(string="Project Cost Estimate Part B")
    partC = fields.Boolean(string="General And Adminstrative Expense")
    ideatime_pic_info = fields.Boolean(string="Ideatime PIC Info")
    project_budget_plan = fields.Boolean(string="Project Budget Applicable Plan")
    batch = fields.Boolean(string="Budget Batch Line")
