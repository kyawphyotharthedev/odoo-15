# -*- coding: utf-8 -*-

from odoo import models, fields


class StockReport(models.TransientModel):
    _name = "wizard.stock.history"
    _description = "Current Stock History"

    location_id = fields.Many2many('stock.location', string='Warehouse Location', required=True)

    def export_xls(self):
        self.ensure_one()
        data = {'form': self.read(['location_id'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'current_stock_xlsx_report.stock_report_xls.xlsx'), ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=data)
