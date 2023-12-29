from odoo import models, fields


class SaleItemReport(models.TransientModel):
    _name = "saleitem.report"
    _description = "Sale Item Report"

    cate_group_id = fields.Many2many('service.category.group', string="Service Group")
    cate_sector_id = fields.Many2one('service.category.sector', string="Service Sector")
    is_sale_item = fields.Boolean(default=True)
    product_variant = fields.Boolean()

    def print_report(self):
        self.ensure_one()
        data = {'form': self.read(['cate_group_id', 'cate_sector_id', 'is_sale_item', 'product_variant'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'ideatime_core.saleitem_report_xlsx'), ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=data)

    def print_pdf_report(self):
        return self.env.ref('ideatime_core.action_sale_item_report').report_action(self)

    def search_product(self):
        query_string = [('is_sale_item', '=', True)]
        if self.cate_sector_id:
            query_string.append(('cate_sector_id', '=', self.cate_sector_id.id))

        get_product_line = self.env['product.template'].search(query_string, order='cate_sector_id')

        product = []
        count = 1
        for line in get_product_line:
            data = {
                'no': count,
                'photo': line.image_medium,
                'item_name': line.name,
                'item_code': line.barcode,
                'unit': line.uom_id.name,
                'variants': line.attribute_line_ids,
                'cost_extra': 0,
                'sale_price': line.list_price
            }
            product.append(data)
            count += 1
        return product
