from odoo import models


class PurchasePrice(models.AbstractModel):
    _name = 'report.ideatime_core.saleitem_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Sale Item Report'

    def get_service_sector(self, data):
        cate_sector_id = data['form'].get('cate_sector_id')
        return cate_sector_id

    def generate_xlsx_report(self, workbook, data, objects):

        sheet = workbook.add_worksheet()
        format3 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format4 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True})

        service_sector_range = self.get_service_sector(data)
        query_string = [('is_sale_item', '=', data['form'].get('is_sale_item'))]
        if service_sector_range:
            query_string.append(('cate_sector_id', 'in', service_sector_range))

        get_product_line = self.env['product.template'].search(query_string, order='cate_sector_id')
        heading_row = 0
        sheet.write(heading_row, 0, 'No', format3)
        sheet.write(heading_row, 1, 'Service Group', format3)
        sheet.write(heading_row, 2, 'Service Sector', format3)
        sheet.write(heading_row, 3, 'Item name', format3)
        sheet.write(heading_row, 4, 'Reference code', format3)
        sheet.write(heading_row, 5, 'Unit', format3)
        sheet.write(heading_row, 6, 'Unit Pirce', format3)
        sheet.write(heading_row, 7, 'Variants', format3)
        sheet.write(heading_row, 8, '', format3)

        display_row = heading_row + 1

        column = 0
        sr = 1
        for data in get_product_line:

            sheet.write(display_row, column, sr, format4)
            column += 1
            sheet.write(display_row, column, data.cate_group_id.name, format4)
            column += 1
            sheet.write(display_row, column, data.cate_sector_id.name, format4)
            column += 1
            sheet.write(display_row, column, data.name, format4)
            column += 1
            sheet.write(display_row, column, data.barcode, format4)
            column += 1
            sheet.write(display_row, column, data.uom_id.name, format4)
            column += 1
            sheet.write(display_row, column, data.list_price, format4)
            column += 1

            new_column = column
            sr += 1
            for line in data.attribute_line_ids:
                sheet.write(display_row, new_column, line.attribute_id.name, format4)
                new_column += 1
                for value_line in line.value_ids:
                    sheet.write(display_row, new_column, value_line.name, format4)
                    display_row += 1
                new_column = column
                display_row += 1

            column = 0
