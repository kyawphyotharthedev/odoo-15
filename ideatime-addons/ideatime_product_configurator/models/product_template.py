# -*- coding: utf-8 -*-

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist,
                                                                 parent_combination, only_template)

        res['onhand_quantity'] = self.qty_available
        res['uom'] = self.uom_id.name
        return res
