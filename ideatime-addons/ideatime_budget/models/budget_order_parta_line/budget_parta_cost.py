from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare

class BudgetPartACost(models.Model):
    _name = 'budget.parta.cost'
    _description = 'Budget Part A Cost'


    volume_weight = fields.Float(string='Result', default=1, copy=False, digits=(12, 3))

    # uom field for  Calculate CBM form
    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')
    budget_calculator_line = fields.One2many('budget.calculator.line', 'parta_cost_line_id')
    volume_weight_total = fields.Float(compute="_compute_volume_weight_total", string="Total")


    product_id = fields.Many2one('product.product', required=True, string='Item')
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    on_hand = fields.Float(string='On Hand', compute="_compute_sale")
    budget_order_line_id = fields.Many2one('approval.budget.order.line')
    total_amount = fields.Float(compute="_compute_total_amount", readonly=True)
    payment_type = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], default='cash')
    usage_type = fields.Selection(
        [('self', 'Self Purchase'), ('proc', 'Procurement Purchase'), ('deli', 'Stock Delivery'),
         ('manu', 'Manufacturing Order')], 'Type',
        default='self')
    # fields for Batch Line
    batch_check = fields.Boolean()
    budget_batch_line_id = fields.One2many('budget.batch.line', 'budget_parta_cost_id')

    order_id = fields.Many2one(related='budget_order_line_id.approval_budget_id', store=True, string='Order Reference',
                               readonly=True)
    project_id = fields.Many2one(related='budget_order_line_id.project_id', store=True, string='Project Reference',
                                 readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)
    budget_dir_move_ids = fields.One2many('stock.move', 'budgetdir_line_id')
    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer",
        oldname="delay")
    display_type = fields.Selection([
        # ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)],
                               ondelete='restrict')
    name = fields.Char(string='Name')

    cost_type_id = fields.Many2one('cost.type', string='Cost Type', required=True)

    # move_ids = fields.One2many('stock.move', 'request_line_id', string='Reservation', readonly=True, copy=False)
    # move_ids = fields.One2many('stock.move', 'created_budgetdir_line_id', 'Downstream Moves')
    

    def _create_stock_moves(self, picking):
        values = []
        for line in self:
            for val in line._prepare_stock_moves(picking):
                values.append(val)

        return self.env['stock.move'].create(values)
    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu'] and self.usage_type != 'manu':
            return res
        if self.usage_type == 'manu':
            extra_move_vals = self._prepare_stock_move_vals(picking)
        # extra_move_vals['move_ids'] = False
            res.append(extra_move_vals)
        return res
    def _prepare_stock_move_vals(self,picking):
        self.ensure_one()
        product = self.product_id
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'product_id': self.product_id.id,
            'name':self.product_id.name,
            'picking_id': picking.id,
            'company_id': self.order_id.company_id.id,
            'picking_type_id': self.order_id.warehouse_id.int_type_id.id,
            'origin': self.order_id.name,
            'location_id':self.order_id.warehouse_id.int_type_id.default_location_src_id.id,
            'location_dest_id':self.order_id.warehouse_id.int_type_id.default_location_dest_id.id,
            'warehouse_id': self.order_id.warehouse_id.id,
            'product_uom_qty': self.qty,
            'product_uom': self.product_uom.id,
        }


    @api.depends('qty')
    def _compute_amount(self):
        for line in self:
            line.product_uom_qty = 0.0
            if line.qty:
                line.product_uom_qty = line.qty


    @api.depends('budget_calculator_line')
    def _compute_volume_weight_total(self):
        for record in self:
            record.volume_weight_total = 0
            for line in record.budget_calculator_line:
                record.volume_weight_total += line.volume_weight




    # Calculate CBM function

    def calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_budget.view_budget_direct_material_cost_cbm').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'budget.parta.cost',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, customer_lead=0)

        lines = super().create(vals_list)
        for line in lines:
            if line.product_id:
                msg = _("Extra line with %s ") % (line.product_id.display_name,)
                line.order_id.message_post(body=msg)
                # create an analytic account if at least an expense product
                if line.product_id.expense_policy not in [False, 'no'] and not line.order_id.analytic_account_id:
                    line.order_id._create_analytic_account()
        return lines

    def save(self):
        # print('Budget Direct Material Cost Qty ', self.volume_weight)
        self.qty = self.volume_weight_total
        return {'type': 'ir.actions.act_window_close'}

    def _update_line_quantity(self, values):
        orders = self.mapped('order_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.order_id == order)
            msg = "<b>The ordered quantity has been updated.</b><ul>"
            for line in order_lines:
                msg += "<li> %s:" % (line.product_id.display_name,)
                msg += "<br/>" + _("Ordered Quantity") + ": %s -> %s <br/>" % (
                    line.product_uom_qty, float(values['product_uom_qty']),)

                if line.product_id.type in ('consu', 'product'):
                    msg += _("Delivered Quantity") + ": %s <br/>" % (line.qty_delivered,)
                msg += _("Invoiced Quantity") + ": %s <br/>" % (line.qty_invoiced,)
            msg += "</ul>"
            order.message_post(body=msg)

    @api.onchange('qty_delivered')
    def _inverse_qty_delivered(self):
        """ When writing on qty_delivered, if the value should be modify manually (`qty_delivered_method` = 'manual' only),
            then we put the value in `qty_delivered_manual`. Otherwise, `qty_delivered_manual` should be False since the
            delivered qty is automatically compute by other mecanisms.
        """
        for line in self:
            if line.qty_delivered_method == 'manual':
                line.qty_delivered_manual = line.qty_delivered
            else:
                line.qty_delivered_manual = 0.0

    @api.onchange('product_id')
    def _compute_sale(self):
        for record in self:
            # record.cost = record.product_id.standard_price
            record.on_hand = record.product_id.qty_available

    @api.onchange('product_id')
    def product_id_change(self):

        if not self.product_id:
            return {'domain': {'product_uom': []}}


        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        result = {'domain': domain}
        warning = {}

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        self.unit_price = self.product_id.standard_price
        self.customer_lead = self.product_id.sale_delay

        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        self._onchange_product_id_check_availability()

        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        # self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message = _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                              (self.product_uom_qty, self.product_uom.name, self.product_id.name,
                               product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available,
                                     precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                   (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message': message
                    }
                    return {'warning': warning_mess}
        return {}

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(
                        product, qty, self.order_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
            if pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = product_currency or (
                product.company_id and product.company_id.currency_id) or self.env.user.company_id.currency_id
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id,
                                                              self.company_id or self.env.user.company_id,
                                                              self.order_id.date_order or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _get_protected_fields(self):
        return [
            'product_id', 'name', 'price_unit', 'product_uom', 'product_uom_qty',
            'tax_id', 'analytic_tag_ids'
        ]

    @api.depends('budget_dir_move_ids')
    def _compute_product_updatable(self):
        for line in self:
            if not line.budget_dir_move_ids.filtered(lambda m: m.state != 'cancel'):
                super(BudgetPartACost, line)._compute_product_updatable()
            else:
                line.product_updatable = False

    @api.onchange('product_packaging')
    def _onchange_product_packaging(self):
        if self.product_packaging:
            return self._check_package()

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                # date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)

    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """

        # values = super(OrderLineLotBOQ, self)._prepare_procurement_values(group_id)
        values = {}
        self.ensure_one()
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'budgetdir_line_id': self.id,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
            'partner_dest_id': self.order_id.partner_shipping_id,
        })

        return values

    def _get_qty_procurement(self):
        self.ensure_one()
        qty = 0.0
        for move in self.budget_dir_move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code == 'outgoing':
                qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom,
                                                          rounding_method='HALF-UP')
            elif move.picking_code == 'incoming':
                qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom,
                                                          rounding_method='HALF-UP')
        return qty
    


    def _action_launch_stock_rule(self):
        if self._context.get("skip_procurement"):
            return True
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.product_id.type not in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name,
                    'move_type': line.order_id.picking_policy,
                    'budget_id': line.order_id.id,
                    'project_id': line.project_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_id, product_qty, procurement_uom,
                line.order_id.partner_id.property_stock_customer,
                line.order_id.name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)
        return True
    


    def _check_routing(self):
        """ Verify the route of the product based on the warehouse
            return True if the product availibility in stock does not need to be verified,
            which is the case in MTO, Cross-Dock or Drop-Shipping
        """
        is_available = False
        product_routes = self.route_id or (self.product_id.route_ids + self.product_id.categ_id.total_route_ids)

        # Check MTO
        wh_mto_route = self.order_id.warehouse_id.mto_pull_id.route_id
        if wh_mto_route and wh_mto_route <= product_routes:
            is_available = True
        else:
            mto_route = False
            try:
                mto_route = self.env['stock.warehouse']._find_global_route('stock.route_warehouse0_mto',
                                                                           _('Make To Order'))
            except UserError:
                # if route MTO not found in ir_model_data, we treat the product as in MTS
                pass
            if mto_route and mto_route in product_routes:
                is_available = True

        # Check Drop-Shipping
        if not is_available:
            for pull_rule in product_routes.mapped('rule_ids'):
                if pull_rule.picking_type_id.sudo().default_location_src_id.usage == 'supplier' and \
                        pull_rule.picking_type_id.sudo().default_location_dest_id.usage == 'customer':
                    is_available = True
                    break

        return is_available
    def _update_line_quantity(self, values):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        line_products = self.filtered(lambda l: l.product_id.type in ['product', 'consu'])
        if line_products.mapped('qty_delivered') and float_compare(values['product_uom_qty'],
                                                                   max(line_products.mapped('qty_delivered')),
                                                                   precision_digits=precision) == -1:
            raise UserError(_('You cannot decrease the ordered quantity below the delivered quantity.\n'
                              'Create a return first.'))
        super(BudgetPartACost, self)._update_line_quantity(values)

    def create_batch(self):

        batch_lines = []
        for rec in self.budget_order_line_id:
            for record in rec.approval_budget_id:
                if record.budget_line_id:
                    for batch_line in record.budget_line_id:
                        batch_lines.append((0, 0, {
                            'budget_id': batch_line.approval_budget_id.id,
                            'batch_id': batch_line.id,

                        }))
                    self.budget_batch_line_id = batch_lines
                    self.budget_batch_line_id[0]['product_uom_qty'] = self.qty
                    self.budget_batch_line_id[0]['total_amount'] = self.total_amount
                    self.batch_check = True

    @api.depends('unit_price', 'qty')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = line.unit_price * line.qty

    def open_batch(self):
        action_ctx = dict(self.env.context)
        action_ctx['default_budget_id'] = self.order_id.id
        view_id = self.env.ref('ideatime_budget.view_budget_direct_batch').id
        return {
            'name': ('Batch Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'budget.parta.cost',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx,

        }
