from odoo import api, fields, models, _

# from datetime import date, timedelta
from datetime import datetime, timedelta


class AccountMove(models.Model):
    _inherit = "account.move"
    paid_amount = fields.Monetary(string='Total Paid Amount', store=True, readonly=True,
                                          compute='compute_paid_amount', currency_field='company_currency_id')
    @api.depends('amount_residual_signed','amount_total_signed')
    def compute_paid_amount(self):
        for line in self:
            line.paid_amount = line.amount_total_signed - line.amount_residual_signed


