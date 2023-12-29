from odoo import models


class PurchasePrice(models.AbstractModel):
    _name = 'report.ideatime_purchase.purchase_price_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Purchase Price History'

    def get_date_range(self, data):
        date_from = data['form'].get('date_from')
        date_to = data['form'].get('date_to')

        return date_from, date_to

    def get_product_range(self, data):
        product_ids = data['form'].get('product_ids')
        return product_ids

    def generate_xlsx_report(self, workbook, data, objects):

        sheet = workbook.add_worksheet()

        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'center',
             'valign': 'vcenter', 'bold': True})
        format2 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'right': False, 'left': False, 'bottom': False, 'top': False,
             'bold': True})
        format3 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format4 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True})
        date_range = self.get_date_range(data)
        product_range = self.get_product_range(data)
        query_string = []
        if product_range:
            query_string.append(('product_id', 'in', product_range))

        get_purchase_order_line = self.env['purchase.order.line'].search(query_string)
        sheet.merge_range(0, 0, 0, 12, 'Purchase Price History ' + date_range[0] + ' TO ' + date_range[1], format2)
        heading_row = 2
        sheet.write(heading_row, 0, 'Product Name', format3)
        sheet.write(heading_row, 1, 'Purchase Date', format3)
        sheet.write(heading_row, 2, 'Vendor', format3)
        sheet.write(heading_row, 3, 'Purchase', format3)
        sheet.write(heading_row, 4, 'Qty', format3)
        sheet.write(heading_row, 5, 'Price', format3)
        sheet.write(heading_row, 6, 'UOM', format3)
        display_row = heading_row + 1

        for purchase in get_purchase_order_line.search([('product_id', 'in', product_range)]):

            if date_range[0] <= str(purchase.order_id.date_order) <= date_range[1]:
                sheet.write(display_row, 0, purchase.name, format4)
                sheet.write(display_row, 1, purchase.order_id.date_order.strftime('%d-%m-%Y'), format4)
                sheet.write(display_row, 2, purchase.order_id.partner_id.name, format4)
                sheet.write(display_row, 3, purchase.order_id.name, format4)
                sheet.write(display_row, 4, purchase.product_qty, format4)
                sheet.write(display_row, 5, purchase.price_unit, format4)
                sheet.write(display_row, 6, purchase.product_uom.name, format4)

            display_row += 1
