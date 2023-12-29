# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class ProductConfiguratorController(http.Controller):

    @http.route(['/ideatime_product_configurator/store_cost_type'], type='json', auth="user", methods=['POST'])
    def store_cost_type(self, cost_type_id, **kw):

        return request.env['ir.ui.view']._render_template(
            "ideatime_product_configurator.product_configurator_store_cost_type", {
                'cost_type_id': cost_type_id
            })
    @http.route(['/ideatime_product_configurator/configure'], type='json', auth="user", methods=['POST'])
    def configure(self, product_id, pricelist_id, **kw):
        add_qty = int(kw.get('add_qty', 1))
        product_template = request.env['product.template'].browse(int(product_id))
        to_currency = product_template.currency_id
        pricelist = self._get_pricelist(pricelist_id)

        if pricelist:
            product_template = product_template.with_context(pricelist=pricelist.id,
                                                             partner=request.env.user.partner_id)
            to_currency = pricelist.currency_id

        return request.env['ir.ui.view']._render_template(
            "ideatime_product_configurator.product_configurator_configure", {
                'product': product_template,
                # to_currency deprecated, get it from the pricelist or product directly
                'to_currency': to_currency,
                'pricelist': pricelist,
                'add_qty': add_qty,
                # get_attribute_exclusions deprecated, use product method
                'get_attribute_exclusions': self._get_attribute_exclusions
            })

    @http.route(['/product_configurator/get_combination_info'], type='json', auth="user", methods=['POST'])
    def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        combination = request.env['product.template.attribute.value'].browse(combination)
        pricelist = self._get_pricelist(pricelist_id)
        ProductTemplate = request.env['product.template']
        if 'context' in kw:
            ProductTemplate = ProductTemplate.with_context(**kw.get('context'))
        product_template = ProductTemplate.browse(int(product_template_id))
        res = product_template._get_combination_info(combination, int(product_id or 0), int(add_qty or 1), pricelist)
        if 'parent_combination' in kw:
            parent_combination = request.env['product.template.attribute.value'].browse(kw.get('parent_combination'))
            if not combination.exists() and product_id:
                product = request.env['product.product'].browse(int(product_id))
                if product.exists():
                    combination = product.product_template_attribute_value_ids
            res.update({
                'is_combination_possible': product_template._is_combination_possible(combination=combination,
                                                                                     parent_combination=parent_combination),
            })
        return res

    @http.route(['/product_configurator/create_product_variant'], type='json', auth="user", methods=['POST'])
    def create_product_variant(self, product_template_id, product_template_attribute_value_ids, **kwargs):
        return request.env['product.template'].browse(int(product_template_id)).create_product_variant(
            product_template_attribute_value_ids)

    def _get_attribute_exclusions(self, product, reference_product=None):
        """deprecated, use product method"""
        parent_combination = request.env['product.template.attribute.value']
        if reference_product:
            parent_combination |= reference_product.product_template_attribute_value_ids
            if reference_product.env.context.get('no_variant_attribute_values'):
                # Add "no_variant" attribute values' exclusions
                # They are kept in the context since they are not linked to this product variant
                parent_combination |= reference_product.env.context.get('no_variant_attribute_values')
        return product._get_attribute_exclusions(parent_combination)

    def _get_product_context(self, pricelist=None, **kw):
        """deprecated, can be removed in master"""
        product_context = dict(request.context)
        if pricelist:
            if not product_context.get('pricelist'):
                product_context['pricelist'] = pricelist.id
            product_context.update(kw.get('kwargs', {}).get('context', {}))

        return product_context

    def _get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist, **kw):
        """deprecated, use product method"""
        combination = request.env['product.template.attribute.value'].browse(combination)
        return request.env['product.template'].browse(product_template_id)._get_combination_info(combination,
                                                                                                 product_id, add_qty,
                                                                                                 pricelist)

    def _get_pricelist(self, pricelist_id, pricelist_fallback=False):
        return request.env['product.pricelist'].browse(int(pricelist_id or 0))
