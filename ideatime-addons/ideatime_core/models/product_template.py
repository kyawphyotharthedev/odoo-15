import itertools
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('cate_group_id', 'cate_sector_id', 'cate_line_id', 'cate_particular_id', 'cate_option_id',
                  'material_group_id', 'material_sector_id', 'material_category_id', 'material_sub_category_id',
                  'material_particular_id', 'material_classification_id', 'material_type_id', 'material_function_id',
                  'material_steamline_id')
    def _compute_display_type(self):
        if self.is_sale_item:
            saleitem_display_type = [self.cate_group_id.name or '', self.cate_sector_id.name or '',
                                     self.cate_line_id.name or '', self.cate_particular_id.name or '',
                                     self.cate_function_id.name or '', self.cate_option_id.name or '']

            self.display_type = "/ ".join(filter(None, saleitem_display_type))
        if self.is_material:
            material_display_type = [self.material_group_id.name or '', self.material_sector_id.name or '',
                                     self.material_category_id.name or '', self.material_sub_category_id.name or '',
                                     self.material_particular_id.name or '', self.material_classification_id.name or '',
                                     self.material_type_id.name or '', self.material_function_id.name or '',
                                     self.material_steamline_id.name or '']
            self.display_type = "/ ".join(filter(None, material_display_type))

    @api.onchange('cate_group_id', 'cate_sector_id', 'cate_line_id', 'cate_particular_id', 'cate_function_id',
                  'cate_option_id')
    def _compute_sale_item_code_name(self):
        if self.cate_option_id:
            if self.cate_option_id.is_innovative:
                self.is_innovative = True
            else:
                self.is_innovative = False

        name_list = [self.cate_particular_id.name or '', self.cate_function_id.name or '',
                     self.cate_option_id.name or '']

        self.name = "_".join(str(name) for name in filter(lambda n: n != '', name_list))

    @api.onchange('is_material')
    def _is_material_change(self):
        if self.is_material:
            self.is_service_item = False
            self.is_sale_item = False
            self.detailed_type = 'product'

    @api.onchange('is_sale_item')
    def _is_sale_item_change(self):
        if self.is_sale_item:
            self.is_material = False
            self.is_service_item = False
            self.detailed_type = 'service'

    @api.onchange('is_service_item')
    def _is_service_item_change(self):
        if self.is_service_item:
            self.is_material = False
            self.is_sale_item = False
            self.detailed_type = 'service'

    display_type = fields.Text(string="Display Type")
    list_price = fields.Float(
        'Sales Price', default=0.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.")

    cate_group_id = fields.Many2one('service.category.group', string='Service Group')
    cate_sector_id = fields.Many2one('service.category.sector', string='Service Sector')
    cate_line_id = fields.Many2one('service.category.line', string='Service Line')
    cate_particular_id = fields.Many2one('service.category.particular', string='Service Category Particular')
    cate_function_id = fields.Many2one('service.category.function', string='Service Category Function')
    cate_option_id = fields.Many2one('service.category.option', string='Option')

    is_material = fields.Boolean(string='Material', default=False)
    is_sale_item = fields.Boolean(string='Sale Item', default=False)
    is_return_product = fields.Boolean(string="Return Product")
    is_service_item = fields.Boolean(string="Service", default=False)
    is_manual_item = fields.Boolean(string='Manual Item')

    customer_name = fields.Char('Customer Name')
    is_innovative = fields.Boolean()
    product_intro = fields.Text('Product Intro')
    product_spec = fields.Text('Product Specification')

    sale_item_categ_id = fields.Many2one('sale.item.category', string='Sale Item Category')

    item_sample_photo_line_ids = fields.One2many('item.sample.photo.line', 'product_id')
    material_sample_photo_line_ids = fields.One2many('material.sample.photo.line', 'product_id')
    process_install_sample_photo_line_ids = fields.One2many('process_install.sample.photo.line', 'product_id')
    item_intro_ids = fields.One2many('item.intro', 'product_id')
    moq_ids = fields.One2many('min.of.qty', 'product_id')
    product_env_qty_std_ids = fields.One2many('product.env_quality_std', 'product_id')
    other_supplement_info_ids = fields.One2many('other.supplement.info', 'product_id')
    item_spec_ids = fields.One2many('item.spec', 'product_id')
    particular_temp_id = fields.Many2one('item.spec.particular.template', string="Particular Template")
    item_quality_ids = fields.One2many('item.quality', 'product_id')
    warrenty_period_ids = fields.One2many('warrenty.period', 'product_id')
    warrenty_factor_ids = fields.One2many('warrenty.factor', 'product_id')
    main_material_spec_ids = fields.One2many('main.material.spec', 'product_id')
    support_material_spec_ids = fields.One2many('support.material.spec', 'product_id')
    production_craft_install_ids = fields.One2many('production.craft.install', 'product_id')
    production_process_ids = fields.One2many('production.process', 'product_id')
    install_process_ids = fields.One2many('installation.process', 'product_id')
    material_qc_process_ids = fields.One2many('material.qc.process', 'product_id')
    production_qc_process_ids = fields.One2many('production.qc.process', 'product_id')
    install_qc_process_ids = fields.One2many('installation.qc.process', 'product_id')
    service_qc_process_ids = fields.One2many('service.qc.process', 'product_id')
    bep_sale_target_ids = fields.One2many('bep.sale.target', 'product_id')

    calculation_method = fields.Char('Calculation_method')
    unit = fields.Char('Unit')
    usage = fields.Text('Usage')

    material_sector_id = fields.Many2one('material.sector', string='Sector')
    material_group_id = fields.Many2one('material.group', string='Group')
    material_category_id = fields.Many2one('material.category', string='Category')
    material_sub_category_id = fields.Many2one('material.sub.category', string='Sub Category')
    material_classification_id = fields.Many2one('material.classification', string='Classification')
    material_sub_grade_id = fields.Many2one('material.sub.grade', string='Sub Grade')
    material_particular_id = fields.Many2one('material.particular', string='Material Particular')
    material_type_id = fields.Many2one('material.type', string='Material Type')
    material_function_id = fields.Many2one('material.function', string='Material Function')
    material_steamline_id = fields.Many2one('material.steamline', string='Steamline')
    is_indirect_material = fields.Boolean(string="Indirect Material")

    attribute_ids = fields.Many2many('product.attribute', compute="_compute_attribute")

    cost_type_id = fields.Many2many('cost.type', string='Cost Type')

    @api.onchange('particular_temp_id')
    def onchange_particular_temp_id(self):
        self.item_spec_ids = False

        for temp_line in self.particular_temp_id:
            particular_lines = []

            for line in temp_line.particular_template_line:
                particular_lines.append((0, 0, {
                    'display_type': line.display_type,
                    'item_spec_part_title_id': line.item_spec_part_title_id.id,
                    'particular_id': line.particular_id.id,

                }))

            self.item_spec_ids = particular_lines

    def _compute_attribute(self):
        for record in self:
            attribute_ids = []
            for variant_line in record.attribute_line_ids:
                attribute_ids.append(variant_line.attribute_id.id)

            record.attribute_ids = self.env['product.attribute'].search([('id', 'in', attribute_ids)])

    def _create_variant_ids(self):
        self.flush()
        Product = self.env["product.product"]

        variants_to_create = []
        variants_to_activate = Product
        variants_to_unlink = Product

        for tmpl_id in self:
            lines_without_no_variants = tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()

            all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(
                lambda p: (p.active, -p.id))

            current_variants_to_create = []
            current_variants_to_activate = Product

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            single_value_lines = lines_without_no_variants.filtered(
                lambda ptal: len(ptal.product_template_value_ids._only_active()) == 1)
            if single_value_lines:
                for variant in all_variants:
                    combination = variant.product_template_attribute_value_ids | single_value_lines.product_template_value_ids._only_active()
                    # Do not add single value if the resulting combination would
                    # be invalid anyway.
                    if (
                            len(combination) == len(lines_without_no_variants) and
                            combination.attribute_line_id == lines_without_no_variants
                    ):
                        variant.product_template_attribute_value_ids = combination

            # Set containing existing `product.template.attribute.value` combination
            existing_variants = {
                variant.product_template_attribute_value_ids: variant for variant in all_variants
            }

            # Determine which product variants need to be created based on the attribute
            # configuration. If any attribute is set to generate variants dynamically, skip the
            # process.
            # Technical note: if there is no attribute, a variant is still created because
            # 'not any([])' and 'set([]) not in set([])' are True.
            if not tmpl_id.has_dynamic_attributes():
                # Iterator containing all possible `product.template.attribute.value` combination
                # The iterator is used to avoid MemoryError in case of a huge number of combination.
                all_combinations = itertools.product(*[
                    ptal.product_template_value_ids._only_active() for ptal in lines_without_no_variants
                ])
                # For each possible variant, create if it doesn't exist yet.
                for combination_tuple in all_combinations:
                    combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
                    is_combination_possible = tmpl_id._is_combination_possible_by_config(combination,
                                                                                         ignore_no_variant=True)
                    if not is_combination_possible:
                        continue
                    if combination in existing_variants:
                        current_variants_to_activate += existing_variants[combination]
                    else:
                        current_variants_to_create.append(tmpl_id._prepare_variant_values(combination))
                        if len(current_variants_to_create) > 5000:
                            raise UserError(_(
                                'The number of variants to generate is too high. '
                                'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                'To do so, open the form view of attributes and change the mode of *Create Variants*.'))
                variants_to_create += current_variants_to_create
                variants_to_activate += current_variants_to_activate

            else:
                for variant in existing_variants.values():
                    is_combination_possible = self._is_combination_possible_by_config(
                        combination=variant.product_template_attribute_value_ids,
                        ignore_no_variant=True,
                    )
                    if is_combination_possible:
                        current_variants_to_activate += variant
                variants_to_activate += current_variants_to_activate

            variants_to_unlink += all_variants - current_variants_to_activate

        if variants_to_activate:
            variants_to_activate.write({'active': True})
        if variants_to_create:
            Product.create(variants_to_create)
        if variants_to_unlink:
            variants_to_unlink._unlink_or_archive()
            # prevent change if exclusion deleted template by deleting last variant
            if self.exists() != self:
                raise UserError(
                    _("This configuration of product attributes, values, and exclusions would lead to no possible variant. Please archive or delete your product directly if intended."))

        # prefetched o2m have to be reloaded (because of active_test)
        # (eg. product.template: product_variant_ids)
        # We can't rely on existing invalidate_cache because of the savepoint
        # in _unlink_or_archive.
        self.flush()
        self.invalidate_cache()
        return True
