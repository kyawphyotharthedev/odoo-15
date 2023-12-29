# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    # fields for Calculate CBM function
    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Result', default=1, copy=False, digits=(12, 3))

    # uom field for  Calculate CBM form
    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost):
        print("*******************^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^((((((((((((((")
        res = super(StockMove, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty,
                                                                description, svl_id, cost)
        res['project_id'] = self.picking_id.project_id.id or self.production_id.project_id.id
        return res


    def calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_stock.view_inventory_move_line_cbm_calc').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        self.product_uom_qty = self.volume_weight
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)

    barcode = fields.Text(compute="compute_barcode")
    product_uom_label = fields.Char()
    is_indirect_material = fields.Boolean(string="Indirect Material", compute="compute_indirect")
    analytic_account_id = fields.Many2one('account.analytic.account', related="picking_id.analytic_account_id")

    @api.depends('product_id')
    def compute_indirect(self):
        for line in self:
            line.is_indirect_material = False
            if line.product_id:
                line.is_indirect_material = line.product_id.is_indirect_material

    @api.depends('product_id')
    def compute_barcode(self):
        for record in self:
            record.barcode = ''
            if record.product_id:
                record.barcode = record.product_id.barcode

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id.with_context(lang=self.partner_id.lang or self.env.user.lang)
        self.name = product.partner_ref
        self.product_uom = product.uom_id.id
        self.product_uom_label = product.uom_id.uom_label
        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}

    def _get_new_picking_values(self):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking. This method is designed to be inherited. """
        return {
            'origin': self.origin,
            'company_id': self.company_id.id,
            'move_type': self.group_id and self.group_id.move_type or 'direct',
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'project_id': self.group_id and self.group_id.project_id.id,
        }

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id, description):
        # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()

        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(
                    _('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'analytic_account_id': self.analytic_account_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt
