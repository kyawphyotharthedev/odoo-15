from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    budget_approval_id = fields.Many2one('budget.approval', string='Budget')
