from odoo import api, fields, models, _
import time


class PurchasePriceWizard(models.TransientModel):
    _name = 'purchase.price.report'
    _description = 'Purchase Price Report'

    date_from = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    date_to = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    product_ids = fields.Many2many('product.product', string='Products')
    categ_id = fields.Many2many('product.category', string="Product Category")

    def print_report(self):
        self.ensure_one()
        data = {'form': self.read(['date_from', 'date_to', 'product_ids', 'categ_id'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'ideatime_purchase.purchase_price_report_xlsx'),
             ('report_type', '=', 'xlsx')], limit=1).report_action(self, data=data)
