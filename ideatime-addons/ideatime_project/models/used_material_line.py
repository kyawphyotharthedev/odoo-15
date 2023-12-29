from odoo import fields, api, models


class UsedMaterialLine(models.Model):
    _name = 'used.material.line'
    _description = 'Used Material Line'

    @api.onchange('cate_line_id', 'cate_particular_id', 'cate_function_id', 'cate_option_id')
    def _compute_product(self):
        product_obj = self.env['product.product']
        query = [('is_material', '=', True), ('id', 'in', self.project_id.selectable_product_ids.ids)]
        if self.cate_line_id:
            query.append(('cate_line_id', '=', self.cate_line_id.id))
        if self.cate_particular_id:
            query.append(('cate_particular_id', '=', self.cate_particular_id.id))
        if self.cate_function_id:
            query.append(('cate_function_id', '=', self.cate_function_id.id))
        if self.cate_option_id:
            query.append(('cate_option_id', '=', self.cate_option_id.id))
        search_product = product_obj.search(query)
        self.selectable_product_ids = search_product

    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade', index=True,
                                 copy=False)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', digits='Product Unit of Measure',
                                   required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    avg_cost = fields.Float('Avg Cost', digits='Product Price')

    cate_line_id = fields.Many2one('service.category.line', string='Service Line')
    cate_particular_id = fields.Many2one('service.category.particular', string='Particular')
    cate_function_id = fields.Many2one('service.category.function', string='Function')
    cate_option_id = fields.Many2one('service.category.option', string='Option')

    selectable_product_ids = fields.Many2many('product.product', compute="_compute_product")

    @api.onchange('product_id')
    def product_id_change(self):
        self.update({
            'product_uom_qty': 1.0,
            'price_unit': self.product_id.lst_price,
            'name': self.product_id.get_product_multiline_description_sale(),
            'avg_cost': self.product_id.standard_price,
        })

    @api.onchange('product_uom_qty')
    def product_qty_change(self):
        self.update({
            'price_unit': self.product_id.list_price * self.product_uom_qty,
            'avg_cost': self.product_id.standard_price * self.product_uom_qty,
        })
