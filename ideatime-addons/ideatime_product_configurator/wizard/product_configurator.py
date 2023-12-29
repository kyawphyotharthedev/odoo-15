# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductConfigurator(models.TransientModel):
    _name = 'ideatime.product.configurator'
    _description = 'Product Configurator'

    @api.onchange('cate_group_id', 'cate_sector_id', 'cate_line_id', 'cate_particular_id', 'cate_function_id',
                  'cate_option_id', 'group_id', 'sector_id', 'categ_id', 'subcateg_id', 'particular_id',
                  'classification_id', 'type_id', 'function_id', 'streamline_id', 'product_type', 'cost_type_id')
    def _compute_product(self):
        product_obj = self.env['product.template']

        if self.product_type == 'saleitem':
            query = [('is_sale_item', '=', True)]
            if self.cate_group_id:
                query.append(('cate_group_id', '=', self.cate_group_id.id))
            else:
                return product_obj

        elif self.product_type == 'material':
            query = [('is_material', '=', True)]
        else:
            query = [('is_service_item', '=', True)]

        if self.cost_type_id:
            query.append(('cost_type_id', '=', self.cost_type_id.id))
        if self.cate_group_id:
            query.append(('cate_group_id', '=', self.cate_group_id.id))
        if self.cate_sector_id:
            query.append(('cate_sector_id', '=', self.cate_sector_id.id))
        if self.cate_line_id:
            query.append(('cate_line_id', '=', self.cate_line_id.id))
        if self.cate_particular_id:
            query.append(('cate_particular_id', '=', self.cate_particular_id.id))
        if self.cate_function_id:
            query.append(('cate_function_id', '=', self.cate_function_id.id))
        if self.cate_option_id:
            query.append(('cate_option_id', '=', self.cate_option_id.id))
        if self.group_id:
            query.append(('material_group_id', '=', self.group_id.id))
        if self.sector_id:
            query.append(('material_sector_id', '=', self.sector_id.id))
        if self.categ_id:
            query.append(('material_category_id', '=', self.categ_id.id))
        if self.subcateg_id:
            query.append(('material_sub_category_id', '=', self.subcateg_id.id))
        if self.particular_id:
            query.append(('material_particular_id', '=', self.particular_id.id))
        if self.classification_id:
            query.append(('material_classification_id', '=', self.classification_id.id))
        if self.type_id:
            query.append(('material_type_id', '=', self.type_id.id))
        if self.function_id:
            query.append(('material_function_id', '=', self.function_id.id))
        if self.streamline_id:
            query.append(('material_steamline_id', '=', self.streamline_id.id))

        search_product = product_obj.search(query)
        self.selectable_product_ids = search_product

    cate_group_id = fields.Many2one('service.category.group', string='Service Group')
    cate_sector_id = fields.Many2one('service.category.sector', string='Service Sector')
    cate_line_id = fields.Many2one('service.category.line', string='Service Line')
    cate_particular_id = fields.Many2one('service.category.particular', string='Particular')
    cate_function_id = fields.Many2one('service.category.function', string='Function')
    cate_option_id = fields.Many2one('service.category.option', string='Option')

    group_id = fields.Many2one('material.group', string='Group')
    sector_id = fields.Many2one('material.sector', string='Sector')
    categ_id = fields.Many2one('material.category', string='Category')
    subcateg_id = fields.Many2one('material.sub.category', string='Sub Category')
    particular_id = fields.Many2one('material.particular', string='Particular')
    classification_id = fields.Many2one('material.classification', string='Classification')
    type_id = fields.Many2one('material.type', string='Type')
    function_id = fields.Many2one('material.function', string='Function')
    streamline_id = fields.Many2one('material.steamline', string="Streamline")
    product_type = fields.Selection([('saleitem', 'Sale Item'), ('material', 'Purchase Item'), ('service', 'Other')],
                                    string='Product Type',
                                    default='saleitem')

    cost_type_id = fields.Many2one('cost.type', string='Cost Type')

    selectable_product_ids = fields.Many2many('product.template', compute="_compute_product")

    product_template_id = fields.Many2one(
        'product.template', string="Product",
        required=True, domain=[])
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
