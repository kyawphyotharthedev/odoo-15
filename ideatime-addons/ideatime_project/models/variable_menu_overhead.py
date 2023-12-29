from odoo import fields, api, models


class VariableManuOverhead(models.Model):
    _name = 'variable.manu.overhead'
    _inherit = ['used.material.line']
    _description = 'Variable Manu Overhead'

    total_amount = fields.Float('Total', required=True, digits='Product Price', default=0.0)

    @api.onchange('price_unit', 'product_uom_qty')
    def price_onchange(self):
        self.total_amount = self.price_unit * self.product_uom_qty
