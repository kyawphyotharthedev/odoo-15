from odoo import fields, models
import time


class PurchaseDetailWizard(models.TransientModel):
    _name = 'purchase.detail.report'
    _description = 'Purchase Detail Report'

    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    date_to = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    currency_id = fields.Many2many('res.currency', string="Currency", required=True)

    def print_report(self):
        self.ensure_one()
        data = {'form': self.read(['date_from', 'date_to', 'currency_id'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'ideatime_purchase.po_detail_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1).report_action(self, data=data)
