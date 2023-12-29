from odoo import models
import io
import base64


class PurchaseHistoryDetail(models.AbstractModel):
    _name = 'report.ideatime_purchase.po_detail_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Purchase History Detail Report'

    def get_date_range(self, data):
        date_from = data['form'].get('date_from')
        date_to = data['form'].get('date_to')

        return date_from, date_to

    def get_currency_range(self, data):
        currency = data['form'].get('currency_id')
        return currency

    def generate_xlsx_report(self, workbook, data, objects):

        sheet = workbook.add_worksheet()
        format2 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'right': False, 'left': False, 'bottom': False, 'top': False,
             'bold': True})
        format3 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True, 'valign': 'top'})
        format4 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True})

        sheet.set_column(1, 20, 20)
        date_range = self.get_date_range(data)
        currency_range = self.get_currency_range(data)

        sheet.merge_range(0, 0, 0, 12, date_range[0] + ' TO ' + date_range[1], format2)
        heading_row = 2
        sheet.write(heading_row, 0, 'No', format3)
        sheet.write(heading_row, 1, 'Purchase date', format3)
        sheet.write(heading_row, 2, 'Project code', format3)
        sheet.write(heading_row, 3, 'Project name', format3)
        sheet.write(heading_row, 4, 'BA code', format3)
        sheet.write(heading_row, 5, 'PO code', format3)
        sheet.write(heading_row, 6, 'PEC claim code', format3)
        sheet.write(heading_row, 7, 'Vendor', format3)
        sheet.write(heading_row, 8, 'Warehouse No', format3)
        sheet.write(heading_row, 9, 'Currency', format3)

        sheet.write(heading_row, 10, 'Barcode', format3)
        sheet.write(heading_row, 11, 'Item name', format3)
        sheet.write(heading_row, 12, 'Item attribute name', format3)
        sheet.write(heading_row, 13, 'Product type', format3)
        sheet.write(heading_row, 14, 'Order Qty', format3)
        sheet.write(heading_row, 15, 'Received Qty', format3)
        sheet.write(heading_row, 16, 'Unit of Measurement', format3)
        sheet.write(heading_row, 17, 'Unit Price', format3)
        sheet.write(heading_row, 18, 'Total Amount', format3)
        sheet.write(heading_row, 19, 'Photo', format3)
        sheet.write(heading_row, 20, 'Remark', format3)
        display_row = heading_row + 1
        sr = 1
        column = 0

        get_purchse_order = self.env['purchase.order'].search(
            [('date_order', '>=', date_range[0]), ('date_order', '<=', date_range[1]),
             ('currency_id', 'in', currency_range)])
        for data in get_purchse_order:
            sheet.write(display_row, column, sr, format3)
            column += 1
            sheet.write(display_row, column, data.date_order.strftime('%m-%d-%Y'), format3)
            column += 1
            sheet.write(display_row, column, data.project_id.name, format3)
            column += 1
            sheet.write(display_row, column, data.project_name, format3)
            column += 1
            sheet.write(display_row, column, data.budget_id.name or None, format3)
            column += 1
            sheet.write(display_row, column, data.name, format3)
            column += 1
            sheet.write(display_row, column, data.partner_id.name, format3)
            column += 1
            for x in data.picking_ids:
                sheet.write(display_row, column, x.name, format4)
            column += 1
            sheet.write(display_row, column, data.currency_id.name, format3)
            column += 1
            display_row = display_row
            new_column = column

            for line in data.order_line:
                sheet.set_row(display_row, 100)

                sheet.write(display_row, new_column, line.product_id.barcode, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.product_id.name, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.product_id.name_get()[0][1], format3)
                new_column += 1
                product_type = ''
                if line.product_id.type == 'product':
                    product_type = 'Storable Product'
                elif line.product_id.type == 'service':
                    product_type = 'Service'
                elif line.product_id.type == 'consu':
                    product_type = 'Consumable'
                sheet.write(display_row, new_column, product_type, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.product_qty, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.qty_received, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.product_uom.name, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.price_unit, format3)
                new_column += 1
                sheet.write(display_row, new_column, line.price_subtotal, format3)
                new_column += 1
                if line.product_id.image_medium:
                    product_image = io.BytesIO(base64.b64decode(line.product_id.image_medium) or None)
                    sheet.insert_image('T' + str(display_row + 1), 'image.png',
                                       {'image_data': product_image, 'x_scale': 1})
                    new_column += 1
                else:
                    sheet.write(display_row, new_column, '', format3)
                    new_column += 1

                sheet.write(display_row, new_column, line.remark or None, format3)
                new_column += 1
                display_row += 1
                new_column = 10

            column = 0
            display_row = display_row
            sr += 1
