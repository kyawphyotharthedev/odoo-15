# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models


class StockReportXls(models.AbstractModel):
    _name = 'report.current_stock_xlsx_report.stock_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Stock Report XLSX'

    def get_warehouse(self, data):
        location = data['form'].get('location_id')
        return location

    def generate_xlsx_report(self, workbook, data, objects):

        get_warehouse = self.get_warehouse(data)
        get_stock_line = self.env['stock.quant'].search([('location_id', 'in', get_warehouse)])
        comp = self.env.user.company_id.name
        sheet = workbook.add_worksheet('Stock Info')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range(1, 7, 2, 10, 'Product Stock Info', format0)
        sheet.merge_range(3, 7, 3, 10, comp, format11)
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz)
        time = pytz.utc.localize(datetime.now()).astimezone(tz)
        sheet.merge_range('A8:G8', 'Report Date: ' + str(time.strftime("%Y-%m-%d %H:%M %p")), format1)
        sheet.merge_range('A9:G9', 'Product Information', format11)

        sheet.write(9, 0, 'Barcode', format21)
        sheet.write(9, 1, 'Name', format21)
        sheet.write(9, 2, 'Location', format21)
        sheet.write(9, 3, 'Reserved Quantity', format21)
        sheet.write(9, 4, 'On Hand Quantity', format21)
        sheet.write(9, 5, 'Unit of Measure', format21)
        display_row = 10
        for line in get_stock_line:
            sheet.write(display_row, 0, line.product_id.barcode, format21)
            sheet.write(display_row, 1, line.name_get()[0][1], format21)
            sheet.write(display_row, 2, line.location_id.barcode, format21)
            sheet.write(display_row, 3, line.reserved_quantity, format21)
            if line.quantity < 0:

                sheet.write(display_row, 4, line.quantity, red_mark)
            else:
                sheet.write(display_row, 4, line.quantity, format21)

            sheet.write(display_row, 5, line.product_uom_id.name, format21)
            display_row += 1
