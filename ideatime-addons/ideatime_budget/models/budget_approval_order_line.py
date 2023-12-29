# -*- coding: utf-8 -*-

from itertools import groupby

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ApprovalBudgetOrderLine(models.Model):
    _name = 'approval.budget.order.line'
    _description = 'Approval Project Order Line'

    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')
    approval_budget_id = fields.Many2one('budget.approval')
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    invoice_lines = fields.Many2many('account.move.line', 'approval_budget_order_line_invoice_rel', 'order_line_id',
                                     'invoice_line_id', string='Invoice Lines', copy=False)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', store=True, readonly=True, default='no')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

    price_subtotal = fields.Monetary(string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

    price_reduce = fields.Float(string='Price Reduce', digits='Product Price', readonly=True,
                                store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    price_reduce_taxinc = fields.Monetary(string='Price Reduce Tax inc', readonly=True, store=True)
    price_reduce_taxexcl = fields.Monetary(string='Price Reduce Tax excl', readonly=True, store=True)

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict')
    product_updatable = fields.Boolean(string='Can Edit Product', readonly=True, default=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', digits='Product Unit of Measure',
                                   required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_uom_label = fields.Char()
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id',
                                                         string='User entered custom product attribute values')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create variants')

    # Non-stored related field to allow portal user to see the image of the product he has ordered
    product_image = fields.Binary('Product Image', related="product_id.image_1920", store=False, readonly=False)

    qty_delivered_method = fields.Selection([
        ('manual', 'Manual'),
        ('analytic', 'Analytic From Expenses')
    ], string="Method to update delivered qty",
        compute_sudo=True, store=True, readonly=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")
    qty_delivered = fields.Float('Delivered Quantity', copy=False, compute_sudo=True, store=True,
                                 digits='Product Unit of Measure', default=0.0)
    qty_delivered_manual = fields.Float('Delivered Manually', copy=False,
                                        digits='Product Unit of Measure', default=0.0)
    qty_to_invoice = fields.Float(
        string='To Invoice Quantity', store=True, readonly=True,
        digits='Product Unit of Measure')
    qty_invoiced = fields.Float(
        string='Invoiced Quantity', store=True, readonly=True,
        digits='Product Unit of Measure')

    untaxed_amount_invoiced = fields.Monetary("Untaxed Invoiced Amount", compute_sudo=True, store=True)
    untaxed_amount_to_invoice = fields.Monetary("Untaxed Amount To Invoice", compute_sudo=True, store=True)
    currency_id = fields.Many2one('res.currency')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    analytic_line_ids = fields.One2many('account.analytic.line', 'so_line', string="Analytic lines")
    is_expense = fields.Boolean('Is expense',
                                help="Is true if the sales order line comes from an expense or a vendor bills")
    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
                                         " They are not copied when duplicating a sales order.")

    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer",
        tracking=True)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    item_order_confirm_ids = fields.One2many('budget.order.confirm.line', 'budget_order_line_id')
    client_demand_ids = fields.One2many('budget.client.demand.line', 'budget_order_line_id')

    order_line_parta_cost_ids = fields.One2many('budget.parta.cost', 'budget_order_line_id')

    size = fields.Char('Size/Service Specification')
    particular_ids = fields.Many2one('material.particular')

    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Volume Weight', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))
    remark = fields.Char(string="Remark", default="N/A")
    direct_grand_total = fields.Float(readonly=True, compute="_compute_grand_total")

    cost_estimate = fields.Float(readonly=True, compute="_compute_cost_estimate_total")
    state = fields.Selection(string='State', required=True, readonly=True, tracking=True,
                             related="approval_budget_id.state")
    project_id = fields.Many2one(related="approval_budget_id.project_id")
    salesman_id = fields.Many2one(related='approval_budget_id.user_id', store=True, string='Salesperson', readonly=True)
    # currency_id = fields.Many2one(related='approval_budget_id.currency_id', depends=['approval_budget_id.currency_id'],
    #                               store=True, string='Currency', readonly=True)
    company_id = fields.Many2one(related='approval_budget_id.company_id', string='Company', store=True, readonly=True)
    order_partner_id = fields.Many2one(related='approval_budget_id.partner_id', store=True, string='Customer',
                                       readonly=False)

    # cost_type_id = fields.Many2one('cost.type', string='Cost Type', required=True)

    # def get_cost_type_values(self):
    #     cost_type = {}
    #     for line in self.order_line_parta_cost_ids:
    #         val = self._prepare_cost_type_line_vals(line)
    #         key = line.cost_type_id.id  # self.env['cost.type.total'].browse(line.cost_type_id)
    #
    #         if key not in cost_type:
    #             cost_type[key] = val
    #         else:
    #             cost_type[key]['amount'] += val['amount']
    #     return cost_type
    #
    # def _prepare_cost_type_line_vals(self, line):
    #     for ap in self:
    #         vals = {
    #             'approval_budget_order_line_id': ap.id,
    #             'cost_type_id': line.cost_type_id.id,
    #             'cost_type_name': line.cost_type_id.name,
    #             'amount': line.total_amount,
    #             'sequence': 1,
    #         }
    #
    #     return vals

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    @api.depends('direct_grand_total')
    def _compute_cost_estimate_total(self):
        for line in self:
            line.cost_estimate = line.direct_grand_total

    @api.depends('order_line_parta_cost_ids')
    def _compute_grand_total(self):
        for line in self:
            line.direct_grand_total = 0
            if line.order_line_parta_cost_ids:
                for dir_line in line.order_line_parta_cost_ids:
                    line.direct_grand_total += dir_line.total_amount

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.name = self.product_id.name
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        # direct_line_obj = self.env['budget.parta.cost']
        return result

    @api.onchange('product_id')
    def get_bom_products(self):
        for line in self:
            # Clear existing part A cost lines when the product changes
            line.order_line_parta_cost_ids.unlink()

            # Find the BOM related to the selected product
            bom = self.env['mrp.bom'].search([
                ('product_id', '=', line.product_id.id),
                ('product_qty', '=', 1.00)
            ], limit=1)

            if bom:
                order_line_parta_cost_vals = []

                for bom_line in bom.bom_line_ids:
                    order_line_parta_cost_vals.append({
                        'product_id': bom_line.product_id.id,
                        'qty': line.product_uom_qty * bom_line.product_qty,
                        'product_uom': bom_line.product_uom_id.id,
                        'cost_type_id': bom_line.product_id.cost_type_id.ids[0],
                        'budget_order_line_id': line.id
                    })

                # Create new records in order_line_parta_cost_ids
                line.write({'order_line_parta_cost_ids': [(0, 0, val) for val in order_line_parta_cost_vals]})

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)
        self.product_uom_qty = self.volume_weight

    def calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_budget.view_budget_line_cbm_calc').id

        return {
            'name': ('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'approval.budget.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.approval_budget_id.currency_id, line.product_uom_qty,
                                            product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    # def open_order_agreement(self):
    #     action_ctx = dict(self.env.context)
    #     view_id = self.env.ref('ideatime_budget.view_budget_order_agreement_line').id
    #
    #     return {
    #         'name': ('Additional Information'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'approval.budget.order.line',
    #         'views': [(view_id, 'form')],
    #         'view_id': view_id,
    #         'target': 'new',
    #         'res_id': self.ids[0],
    #         'context': action_ctx
    #     }

    def open_material_cost(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_budget.view_budget_material_cost_line').id

        return {
            'name': ('Material Cost Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'approval.budget.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }


class CostTypeTotal(models.Model):
    _name = 'cost.type.total'

    approval_budget_order_line_id = fields.Many2one('approval.budget.order.line', string='Order Line Reference',
                                                    required=True)
    cost_type_id = fields.Many2one('cost.type', string='Cost Type')
    cost_type_name = fields.Char(string='Cost Type')
    amount = fields.Integer(string="Amount")
    sequence = fields.Integer(string='Sequence')
