from odoo import models
import io
import base64


class MaterialItemTmplReport(models.AbstractModel):
    _name = 'report.ideatime_core.item_template_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Material Item Template Report'

    def get_product_range(self, data):
        product_id = data['form'].get('product_id')
        return product_id

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
             'bold': True, 'valign': 'top'})
        format4 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True})
        heading_row = 0

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 10, 20)

        sheet.write(heading_row, 0, 'No', format3)
        sheet.write(heading_row, 1, 'Barcode', format3)
        sheet.write(heading_row, 2, 'Item name', format3)
        sheet.write(heading_row, 3, 'Unit of measurement', format3)
        sheet.write(heading_row, 4, 'Onhand', format3)
        sheet.write(heading_row, 5, 'Price', format3)
        sheet.write(heading_row, 6, 'Photo', format3)
        sheet.write(heading_row, 7, 'Product type', format3)
        sheet.write(heading_row, 8, 'Product intro', format3)
        sheet.write(heading_row, 9, 'Product specification', format3)
        sheet.write(heading_row, 10, 'Remark', format3)
        product_range = self.get_product_range(data)

        get_product_line = self.env['product.template'].search([('id', 'in', product_range)])
        display_row = heading_row + 1
        sr = 1
        image_width = 100.0
        image_height = 80.0

        cell_width = 64.0
        cell_height = 20.0
        x_scale = cell_width / image_width
        y_scale = cell_height / image_height

        for data in get_product_line:
            sheet.set_row(display_row, 100)
            sheet.write(display_row, 0, sr, format3)
            sheet.write(display_row, 1, data.barcode, format3)

            sheet.write(display_row, 2, data.name, format3)

            sheet.write(display_row, 3, data.uom_id.name, format3)
            sheet.write(display_row, 4, data.qty_available, format3)
            sheet.write(display_row, 5, data.standard_price, format3)
            if data.image_medium:
                product_image = io.BytesIO(base64.b64decode(data.image_medium))

                sheet.insert_image('G' + str(display_row + 1), 'image.png',
                                   {'image_data': product_image, 'x_scale': 0.7})

            else:
                sheet.write(display_row, 6, '', format3)
            if data.type == 'product':
                product_type = 'Storable Product'
            elif data.type == 'service':
                product_type = 'Service'
            elif data.type == 'consu':
                product_type = 'Consumable'
            sheet.write(display_row, 7, product_type, format3)
            # print(data['type'])
            sheet.write(display_row, 8, data.product_intro or None, format3)
            sheet.write(display_row, 9, data.product_spec or None, format3)
            sheet.write(display_row, 10, data.description or None, format3)
            sr += 1
            display_row += 1
