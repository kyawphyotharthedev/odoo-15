# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare


class CalculatorLine(models.Model):
    _name = 'calculator.line'
    _description = 'Calculator Line'

    size = fields.Char('Size/Service Specification', copy=True)
    description = fields.Text(copy=True)
    Pcs = fields.Float(string='Unit', default=1, copy=True, digits=(12, 2))
    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')

    length = fields.Float(string='Length', default=1, copy=True, digits=(12, 2))
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width = fields.Float(string='Width', default=1, copy=True, digits=(12, 2))
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height = fields.Float(string='Height', default=1, copy=True, digits=(12, 2))
    height_uom = fields.Many2one('uom.uom', string='Height UOM')
    volume_weight = fields.Float(string='Result', default=1, copy=True, digits=(12, 2))
    so_line_id = fields.Many2one('sale.order.line', readonly=1)
    state = fields.Selection(string='Status', related='so_line_id.state')
    product_uom = fields.Char(string='UOM', related="so_line_id.product_uom.name")
    uom_type = fields.Selection([
        ('unit', "Unit"),
        ('volume', "Volume"),
        ('liquid', "Liquid")
    ], string='UOM Type', store=True)

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)


class ItemOrderConfirmation(models.Model):
    _name = 'item.order.confirm.line'
    _description = 'Item Order Confirmation Line'

    particular_id = fields.Char(string='Particular')
    description = fields.Text('Description')
    so_line_id = fields.Many2one('sale.order.line')


class ClientDemand(models.Model):
    _name = 'order.client.demand.line'
    _description = 'Client Demand Line'

    particular_id = fields.Char(string='Particular')
    description = fields.Text('Description')
    so_line_id = fields.Many2one('sale.order.line')


class OrderLineDirectMaterialCost(models.Model):
    _name = 'direct.material.cost'
    _description = 'Direct Material Cost'

    @api.onchange('product_id')
    def _compute_sale(self):
        for record in self:
            record.cost = record.product_id.standard_price

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('length', 'width', 'height', 'pcs')
    def _compute_amount(self):
        for line in self:
            if line.length > 0 and line.width > 0 and line.height > 0 and line.pcs > 0:
                line.product_uom_qty = (line.length * line.width * line.height * line.pcs)
                line.qty = line.product_uom_qty

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', required=True, string='Item', domain="[('is_material', '=', True)]")
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")

    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)
    so_line_id = fields.Many2one('sale.order.line')
    order_id = fields.Many2one(related='so_line_id.order_id', store=True, string='Order Reference', readonly=True)
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', readonly=True,
                                       default=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id',
                                                         string='User entered custom product attribute values')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create variants')
    is_expense = fields.Boolean('Is expense',
                                help="Is true if the sales order line comes from an expense or a vendor bills")
    state = fields.Selection(related='order_id.state', string='Order Status', readonly=True, copy=False, store=True)
    direct_move_ids = fields.One2many('stock.move', 'direct_line_id', string='Stock Moves')
    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)],
                               ondelete='restrict')
    qty_delivered_method = fields.Selection([
        ('manual', 'Manual'),
        ('analytic', 'Analytic From Expenses'),
        ('stock_move', 'Stock Moves')
    ], string="Method to update delivered qty", compute='_compute_qty_delivered_method', compute_sudo=True, store=True,
        readonly=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")

    qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered',
                                 inverse='_inverse_qty_delivered', compute_sudo=True, store=True,
                                 digits='Product Unit of Measure', default=0.0)
    qty_delivered_manual = fields.Float('Delivered Manually', copy=False,
                                        digits='Product Unit of Measure', default=0.0)
    qty_to_invoice = fields.Float(
        compute='_get_to_invoice_qty', string='To Invoice Quantity', store=True, readonly=True,
        digits='Product Unit of Measure')
    qty_invoiced = fields.Float(
        compute='_get_invoice_qty', string='Invoiced Quantity', store=True, readonly=True,
        digits='Product Unit of Measure')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_label = fields.Char()
    cost = fields.Float(
        "Cost", digits='Product Unit of Measure')

    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})

    cost_type_id = fields.Many2one('cost.type', string='Cost Type', required=True)

    @api.depends('product_id', 'order_id.state', 'qty_invoiced', 'qty_delivered')
    def _compute_product_updatable(self):
        for line in self:
            if line.state in ['done', 'cancel'] or (
                    line.state == 'sale' and (line.qty_invoiced > 0 or line.qty_delivered > 0)):
                line.product_updatable = False
            else:
                line.product_updatable = True

    def get_sale_order_line_multiline_description_sale(self, product):
        """ Compute a default multiline description for this sales order line.
        This method exists so it can be overridden in other modules to change how the default name is computed.
        In general only the product is used to compute the name, and this method would not be necessary (we could directly override the method in product).
        BUT in event_sale we need to know specifically the sales order line as well as the product to generate the name:
            the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return product.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        See note about `product_no_variant_attribute_value_ids` above the field
        definition: this method is not reliable to recompute the description at
        a later time, it should only be used initially.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        product_attribute_with_is_custom = self.product_custom_attribute_value_ids.mapped(
            'attribute_value_id.attribute_id')

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate)
        for no_variant_attribute_value in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav: ptav.attribute_id not in product_attribute_with_is_custom
        ):
            name += "\n" + no_variant_attribute_value.attribute_id.name + ': ' + no_variant_attribute_value.name

        # display the is_custom values
        for pacv in self.product_custom_attribute_value_ids:
            name += "\n" + pacv.attribute_value_id.attribute_id.name + \
                    ': ' + pacv.attribute_value_id.name + \
                    ': ' + (pacv.custom_value or '').strip()

        return name

    def _get_qty_procurement(self):
        self.ensure_one()
        qty = 0.0
        for move in self.direct_move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code == 'outgoing':
                qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom,
                                                          rounding_method='HALF-UP')
            elif move.picking_code == 'incoming':
                qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom,
                                                          rounding_method='HALF-UP')
        return qty

    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        return {}

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            with self.env.do_in_onchange():
                line = self.new(values)
                line.product_id_change()
                for field in onchange_fields:
                    if field not in values:
                        res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))

        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.order_id.state == 'approve':
                msg = _("Extra line with %s ") % (line.product_id.display_name,)
                line.order_id.message_post(body=msg)
                # create an analytic account if at least an expense product
                if line.product_id.expense_policy not in [False, 'no'] and not line.order_id.analytic_account_id:
                    line.order_id._create_analytic_account()
        return lines

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

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                _("You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type."))

        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'approve' and float_compare(r.product_uom_qty, values['product_uom_qty'],
                                                                 precision_digits=precision) != 0)._update_line_quantity(
                values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('order_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        result = super(OrderLineDirectMaterialCost, self).write(values)
        return result

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        """ Compute and write the delivered quantity of current SO lines, based on their related
            analytic lines.
            :param additional_domain: domain to restrict AAL to include in computation (required since timesheet is an AAL with a project ...)
        """
        result = {}

        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group anaytic lines by product uom and so line
        domain = expression.AND([[('so_line', 'in', self.ids)], additional_domain])
        data = self.env['account.analytic.line'].read_group(
            domain,
            ['so_line', 'unit_amount', 'product_uom_id'], ['product_uom_id', 'so_line'], lazy=False
        )

        # convert uom and sum all unit_amount of analytic lines to get the delivered qty of SO lines
        # browse so lines and product uoms here to make them share the same prefetch
        lines_map = {line.id: line for line in self}
        product_uom_ids = [item['product_uom_id'][0] for item in data if item['product_uom_id']]
        product_uom_map = {uom.id: uom for uom in self.env['uom.uom'].browse(product_uom_ids)}
        for item in data:
            if not item['product_uom_id']:
                continue
            so_line_id = item['so_line'][0]
            so_line = lines_map[so_line_id]
            result.setdefault(so_line_id, 0.0)
            uom = product_uom_map.get(item['product_uom_id'][0])
            if so_line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(item['unit_amount'], so_line.product_uom, rounding_method='HALF-UP')
            else:
                qty = item['unit_amount']
            result[so_line_id] += qty

        return result

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

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.type')
    def _compute_untaxed_amount_invoiced(self):
        """ Compute the untaxed amount already invoiced from the sale order line, taking the refund attached
            the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                `inv_line` is a customer invoice line linked to the SO line
                `ref_line` is a customer credit note (refund) line linked to the SO line
        """
        for line in self:
            amount_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state in ['open', 'in_payment', 'paid']:
                    invoice_date = invoice_line.invoice_id.date_invoice or fields.Date.today()
                    if invoice_line.invoice_id.type == 'out_invoice':
                        amount_invoiced += invoice_line.currency_id._convert(invoice_line.price_subtotal,
                                                                             line.currency_id, line.company_id,
                                                                             invoice_date)
                    elif invoice_line.invoice_id.type == 'out_refund':
                        amount_invoiced -= invoice_line.currency_id._convert(invoice_line.price_subtotal,
                                                                             line.currency_id, line.company_id,
                                                                             invoice_date)
            line.untaxed_amount_invoiced = amount_invoiced

    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered')
    def _compute_untaxed_amount_to_invoice(self):
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.

            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ['sale', 'done']:
                # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
                # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
                # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
                # amount and not zero. Since we compute untaxed amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                if line.product_id.invoice_policy == 'delivery':
                    price_subtotal = line.price_reduce * line.qty_delivered
                else:
                    price_subtotal = line.price_reduce * line.product_uom_qty

                amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced
            line.untaxed_amount_to_invoice = amount_to_invoice

    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        product = self.product_id.with_context(force_company=self.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
        }
        return res

    def invoice_line_create(self, invoice_id, qty):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative (refund).

            .. deprecated:: 12.0
                Replaced by :func:`invoice_line_create_vals` which can be used for creating
                `account.invoice.line` records in batch

            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns recordset of account.invoice.line created
        """
        return self.env['account.move.line'].create(
            self.invoice_line_create_vals(invoice_id, qty))

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                ptav.price_extra and
                ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=no_variant_attributes_price_extra
            )

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                           self.product_uom_qty,
                                                                                           self.product_uom,
                                                                                           self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.user.company_id, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0
            vals['pcs'] = self.pcs or 1.0

            vals['length'] = self.pcs or 1.0

            vals['width'] = self.pcs or 1.0

            vals['height'] = self.pcs or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            pcs=self.pcs,
            length=self.length,
            width=self.width,
            height=self.height,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = self.get_sale_order_line_multiline_description_sale(product)

        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )

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

    @api.depends('state', 'is_expense')
    def _compute_qty_delivered_method(self):
        """ Sale module compute delivered qty for product [('type', 'in', ['consu']), ('service_type', '=', 'manual')]
                - consu + expense_policy : analytic (sum of analytic unit_amount)
                - consu + no expense_policy : manual (set manually on SOL)
                - service (+ service_type='manual', the only available option) : manual

            This is true when only sale is installed: sale_stock redifine the behavior for 'consu' type,
            and sale_timesheet implements the behavior of 'service' + service_type=timesheet.
        """
        for line in self:
            if line.is_expense:
                line.qty_delivered_method = 'analytic'
            elif not line.is_expense and line.product_id.type in ['consu', 'product']:
                line.qty_delivered_method = 'stock_move'
            else:  # service and consu
                line.qty_delivered_method = 'manual'

    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """

        values = {}
        self.ensure_one()
        date_planned = self.order_id.confirmation_date \
                       + timedelta(days=self.customer_lead or 0.0) - timedelta(
            days=self.order_id.company_id.security_lead)
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'direct_line_id': self.id,
            'date_planned': date_planned,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
        })
        for line in self.filtered("order_id.commitment_date"):
            date_planned = fields.Datetime.from_string(line.order_id.commitment_date) - timedelta(
                days=line.order_id.company_id.security_lead)
            values.update({
                'date_planned': fields.Datetime.to_string(date_planned),
            })
        return values

    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if not line.product_id.type in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                    'project_id': line.order_id.project_id.id,
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

            procurement_uom = line.product_uom
            quant_uom = line.product_uom
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
                                                  line.order_id.partner_shipping_id.property_stock_customer, '',
                                                  line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True


class OrderLineInDirectMaterialCost(models.Model):
    _name = 'in.direct.material.cost'
    _description = 'In Direct Material Cost'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('length', 'width', 'height', 'pcs')
    def _compute_amount(self):
        for line in self:
            if line.length > 0 and line.width > 0 and line.height > 0 and line.pcs > 0:
                line.product_uom_qty = (line.length * line.width * line.height * line.pcs)
                line.qty = line.product_uom_qty

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', required=True, string='Item', domain="[('is_material', '=', True)]")
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    so_line_id = fields.Many2one('sale.order.line')
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)
    so_line_id = fields.Many2one('sale.order.line')
    order_id = fields.Many2one(related='so_line_id.order_id', store=True, string='Order Reference', readonly=True)
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', readonly=True,
                                       default=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id',
                                                         string='User entered custom product attribute values')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create variants')
    is_expense = fields.Boolean('Is expense',
                                help="Is true if the sales order line comes from an expense or a vendor bills")
    state = fields.Selection(related='order_id.state', string='Order Status', readonly=True, copy=False, store=True)
    in_direct_move_ids = fields.One2many('stock.move', 'in_direct_line_id', string='Stock Moves')
    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)],
                               ondelete='restrict')
    qty_delivered_method = fields.Selection([
        ('manual', 'Manual'),
        ('analytic', 'Analytic From Expenses'),
        ('stock_move', 'Stock Moves')
    ], string="Method to update delivered qty", compute='_compute_qty_delivered_method', compute_sudo=True, store=True,
        readonly=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")

    qty_delivered = fields.Float('Delivered Quantity', copy=False, compute='_compute_qty_delivered',
                                 inverse='_inverse_qty_delivered', compute_sudo=True, store=True,
                                 digits='Product Unit of Measure', default=0.0)
    qty_delivered_manual = fields.Float('Delivered Manually', copy=False,
                                        digits='Product Unit of Measure', default=0.0)
    qty_to_invoice = fields.Float(
        compute='_get_to_invoice_qty', string='To Invoice Quantity', store=True, readonly=True,
        digits='Product Unit of Measure')
    qty_invoiced = fields.Float(
        compute='_get_invoice_qty', string='Invoiced Quantity', store=True, readonly=True,
        digits='Product Unit of Measure')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_label = fields.Char()
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})

    @api.depends('product_id', 'order_id.state', 'qty_invoiced', 'qty_delivered')
    def _compute_product_updatable(self):
        for line in self:
            if line.state in ['done', 'cancel'] or (
                    line.state == 'sale' and (line.qty_invoiced > 0 or line.qty_delivered > 0)):
                line.product_updatable = False
            else:
                line.product_updatable = True

    def get_sale_order_line_multiline_description_sale(self, product):
        """ Compute a default multiline description for this sales order line.
        This method exists so it can be overridden in other modules to change how the default name is computed.
        In general only the product is used to compute the name, and this method would not be necessary (we could directly override the method in product).
        BUT in event_sale we need to know specifically the sales order line as well as the product to generate the name:
            the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return product.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        See note about `product_no_variant_attribute_value_ids` above the field
        definition: this method is not reliable to recompute the description at
        a later time, it should only be used initially.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        product_attribute_with_is_custom = self.product_custom_attribute_value_ids.mapped(
            'attribute_value_id.attribute_id')

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate)
        for no_variant_attribute_value in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav: ptav.attribute_id not in product_attribute_with_is_custom
        ):
            name += "\n" + no_variant_attribute_value.attribute_id.name + ': ' + no_variant_attribute_value.name

        # display the is_custom values
        for pacv in self.product_custom_attribute_value_ids:
            name += "\n" + pacv.attribute_value_id.attribute_id.name + \
                    ': ' + pacv.attribute_value_id.name + \
                    ': ' + (pacv.custom_value or '').strip()

        return name

    def _get_qty_procurement(self):
        self.ensure_one()
        qty = 0.0
        for move in self.in_direct_move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code == 'outgoing':
                qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom,
                                                          rounding_method='HALF-UP')
            elif move.picking_code == 'incoming':
                qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom,
                                                          rounding_method='HALF-UP')
        return qty

    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        return {}

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit', 'product_uom', 'tax_id']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            with self.env.do_in_onchange():
                line = self.new(values)
                line.product_id_change()
                for field in onchange_fields:
                    if field not in values:
                        res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))

        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.order_id.state == 'approve':
                msg = _("Extra line with %s ") % (line.product_id.display_name,)
                line.order_id.message_post(body=msg)
                # create an analytic account if at least an expense product
                if line.product_id.expense_policy not in [False, 'no'] and not line.order_id.analytic_account_id:
                    line.order_id._create_analytic_account()
        return lines

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

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                _("You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type."))

        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'approve' and float_compare(r.product_uom_qty, values['product_uom_qty'],
                                                                 precision_digits=precision) != 0)._update_line_quantity(
                values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('order_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        result = super(OrderLineInDirectMaterialCost, self).write(values)
        return result

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        """ Compute and write the delivered quantity of current SO lines, based on their related
            analytic lines.
            :param additional_domain: domain to restrict AAL to include in computation (required since timesheet is an AAL with a project ...)
        """
        result = {}

        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group anaytic lines by product uom and so line
        domain = expression.AND([[('so_line', 'in', self.ids)], additional_domain])
        data = self.env['account.analytic.line'].read_group(
            domain,
            ['so_line', 'unit_amount', 'product_uom_id'], ['product_uom_id', 'so_line'], lazy=False
        )

        # convert uom and sum all unit_amount of analytic lines to get the delivered qty of SO lines
        # browse so lines and product uoms here to make them share the same prefetch
        lines_map = {line.id: line for line in self}
        product_uom_ids = [item['product_uom_id'][0] for item in data if item['product_uom_id']]
        product_uom_map = {uom.id: uom for uom in self.env['uom.uom'].browse(product_uom_ids)}
        for item in data:
            if not item['product_uom_id']:
                continue
            so_line_id = item['so_line'][0]
            so_line = lines_map[so_line_id]
            result.setdefault(so_line_id, 0.0)
            uom = product_uom_map.get(item['product_uom_id'][0])
            if so_line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(item['unit_amount'], so_line.product_uom, rounding_method='HALF-UP')
            else:
                qty = item['unit_amount']
            result[so_line_id] += qty

        return result

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

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.type')
    def _compute_untaxed_amount_invoiced(self):
        """ Compute the untaxed amount already invoiced from the sale order line, taking the refund attached
            the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                `inv_line` is a customer invoice line linked to the SO line
                `ref_line` is a customer credit note (refund) line linked to the SO line
        """
        for line in self:
            amount_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state in ['open', 'in_payment', 'paid']:
                    invoice_date = invoice_line.invoice_id.date_invoice or fields.Date.today()
                    if invoice_line.invoice_id.type == 'out_invoice':
                        amount_invoiced += invoice_line.currency_id._convert(invoice_line.price_subtotal,
                                                                             line.currency_id, line.company_id,
                                                                             invoice_date)
                    elif invoice_line.invoice_id.type == 'out_refund':
                        amount_invoiced -= invoice_line.currency_id._convert(invoice_line.price_subtotal,
                                                                             line.currency_id, line.company_id,
                                                                             invoice_date)
            line.untaxed_amount_invoiced = amount_invoiced

    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered')
    def _compute_untaxed_amount_to_invoice(self):
        """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
                total_sol - amount already invoiced
            where Total_sol depends on the invoice policy of the product.

            Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
            come only from the SO lines.
        """
        for line in self:
            amount_to_invoice = 0.0
            if line.state in ['sale', 'done']:
                # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
                # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
                # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
                # amount and not zero. Since we compute untaxed amount, we can use directly the price
                # reduce (to include discount) without using `compute_all()` method on taxes.
                price_subtotal = 0.0
                if line.product_id.invoice_policy == 'delivery':
                    price_subtotal = line.price_reduce * line.qty_delivered
                else:
                    price_subtotal = line.price_reduce * line.product_uom_qty

                amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced
            line.untaxed_amount_to_invoice = amount_to_invoice

    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        product = self.product_id.with_context(force_company=self.company_id.id)
        account = product.property_account_income_id or product.categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
        }
        return res

    def invoice_line_create(self, invoice_id, qty):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative (refund).

            .. deprecated:: 12.0
                Replaced by :func:`invoice_line_create_vals` which can be used for creating
                `account.invoice.line` records in batch

            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns recordset of account.invoice.line created
        """
        return self.env['account.move.line'].create(
            self.invoice_line_create_vals(invoice_id, qty))

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                ptav.price_extra and
                ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=no_variant_attributes_price_extra
            )

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                           self.product_uom_qty,
                                                                                           self.product_uom,
                                                                                           self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.user.company_id, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0
            vals['pcs'] = self.pcs or 1.0

            vals['length'] = self.pcs or 1.0

            vals['width'] = self.pcs or 1.0

            vals['height'] = self.pcs or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            pcs=self.pcs,
            length=self.length,
            width=self.width,
            height=self.height,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = self.get_sale_order_line_multiline_description_sale(product)

        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )

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

    @api.depends('state', 'is_expense')
    def _compute_qty_delivered_method(self):
        """ Sale module compute delivered qty for product [('type', 'in', ['consu']), ('service_type', '=', 'manual')]
                - consu + expense_policy : analytic (sum of analytic unit_amount)
                - consu + no expense_policy : manual (set manually on SOL)
                - service (+ service_type='manual', the only available option) : manual

            This is true when only sale is installed: sale_stock redifine the behavior for 'consu' type,
            and sale_timesheet implements the behavior of 'service' + service_type=timesheet.
        """
        for line in self:
            if line.is_expense:
                line.qty_delivered_method = 'analytic'
            elif not line.is_expense and line.product_id.type in ['consu', 'product']:
                line.qty_delivered_method = 'stock_move'
            else:  # service and consu
                line.qty_delivered_method = 'manual'

    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """

        values = {}
        self.ensure_one()
        date_planned = self.order_id.confirmation_date \
                       + timedelta(days=self.customer_lead or 0.0) - timedelta(
            days=self.order_id.company_id.security_lead)
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'in_direct_line_id': self.id,
            'date_planned': date_planned,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
        })
        for line in self.filtered("order_id.commitment_date"):
            date_planned = fields.Datetime.from_string(line.order_id.commitment_date) - timedelta(
                days=line.order_id.company_id.security_lead)
            values.update({
                'date_planned': fields.Datetime.to_string(date_planned),
            })
        return values

    def _action_launch_stock_rule(self):

        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if not line.product_id.type in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement()

            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                    'project_id': line.order_id.project_id.id,
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

            procurement_uom = line.product_uom
            quant_uom = line.product_uom
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
                                                  line.order_id.partner_shipping_id.property_stock_customer, '',
                                                  line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True


class OrderLineDirectLabourCost(models.Model):
    _name = 'direct.labour.cost'
    _description = 'Direct Labour Cost'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('length', 'width', 'height', 'pcs')
    def _compute_amount(self):
        for line in self:
            if line.length > 0 and line.width > 0 and line.height > 0 and line.pcs > 0:
                line.product_uom_qty = (line.length * line.width * line.height * line.pcs)
                line.qty = line.product_uom_qty

    product_id = fields.Many2one('product.product', required=True, string='Item',
                                 domain="['&', ('type','=','service'),('is_material', '!=', True)]")
    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    so_line_id = fields.Many2one('sale.order.line')


class OrderLineThridPartyCostContractor(models.Model):
    _name = 'thirdparty.cost.contractor'
    _description = 'Third Party Cost Contractor'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('length', 'width', 'height', 'pcs')
    def _compute_amount(self):
        for line in self:
            if line.length > 0 and line.width > 0 and line.height > 0 and line.pcs > 0:
                line.product_uom_qty = (line.length * line.width * line.height * line.pcs)
                line.qty = line.product_uom_qty

    product_id = fields.Many2one('product.product', required=True, string='Item',
                                 domain="['&', ('type','=','service'),('is_material', '!=', True)]")

    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    so_line_id = fields.Many2one('sale.order.line')


class OrderLineThridPartyCostSubContractor(models.Model):
    _name = 'thirdparty.cost.subcontractor'
    _description = 'Third Party Cost SubContractor'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('length', 'width', 'height', 'pcs')
    def _compute_amount(self):
        for line in self:
            if line.length > 0 and line.width > 0 and line.height > 0 and line.pcs > 0:
                line.product_uom_qty = (line.length * line.width * line.height * line.pcs)
                line.qty = line.product_uom_qty

    product_id = fields.Many2one('product.product', required=True, string='Item',
                                 domain="['&', ('type','=','service'),('is_material', '!=', True)]")

    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    so_line_id = fields.Many2one('sale.order.line')


class ProjectCostEstimateLine(models.Model):
    _name = 'expense.order.line'
    _description = 'Expense Order Line'

    # uom field for  Calculate CBM form
    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')

    product_uom_label = fields.Char()

    product_id = fields.Many2one('product.product', string='Product', domain=[('is_material', '=', True)],
                                 change_default=True, ondelete='restrict')
    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Volume Weight', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))

    order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    name = fields.Text(string='Description')

    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    remark = fields.Char(string="Remark", default="N/A")

    product_uom_qty = fields.Float(string='Ordered Quantity', digits='Product Unit of Measure',
                                   required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"), ('line_expense_section', "Expense Section")], default=False,
        help="Technical field for UX purpose.")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id'], store=True, string='Currency',
                                  readonly=True)

    particular_ids = fields.Many2one('expense.order.line.particular')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * line.product_uom_qty

            line.update({
                'price_subtotal': price
            })

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)

        self.product_uom_qty = self.volume_weight

    def expense_calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_sale.view_expense_line_cbm_calc').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'expense.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('particular_ids')
    def particular_ids_onchange(self):
        if self.particular_ids:
            self.name = self.particular_ids.name


class ProjectBudgetApplicationPlan(models.Model):
    _name = 'project.budget.applicable.plan'
    _description = "Project Budget application Plan"

    name = fields.Char()

    description = fields.Many2one('product.product', string="Description")
    amount = fields.Integer(string="Amount")
    currency = fields.Many2one('res.currency', string="Currency")
    applicable_date = fields.Date(string="Applicable date", default=fields.Date.today())
    complete_date = fields.Date(string="Complete date", default=fields.Date.today())
    remark = fields.Text(string="Remark")
    project_budget_applicable_plan_id = fields.Many2one('sale.order', string="PBAP ID")
