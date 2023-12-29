from odoo import models, fields


class MaterialItemReport(models.TransientModel):
    _name = "materialitem.report"
    _description = "Material Item Report"

    product_id = fields.Many2many('product.product', string="Product", domain=[('is_material', '=', True)])

    def print_report(self):
        self.ensure_one()
        data = {'form': self.read(['product_id'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'ideatime_core.materialitem_report_xlsx'), ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=data)


class MaterialItemTemplateReport(models.TransientModel):
    _name = "materialitem.template.report"
    _description = "Material Item Template Report"

    product_id = fields.Many2many('product.template', string="Product", domain=[('is_material', '=', True)])

    def print_report(self):
        self.ensure_one()
        data = {'form': self.read(['product_id'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'ideatime_core.item_template_report_xlsx'),
             ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=data)
