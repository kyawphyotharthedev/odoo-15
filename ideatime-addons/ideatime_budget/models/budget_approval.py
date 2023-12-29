# -*- coding: utf-8 -*-
from datetime import timedelta
from itertools import groupby

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class BranchDescription(models.Model):
    _name = 'branch.description'
    _description = 'Branch Description'

    name = fields.Char()


class BudgetApproval(models.Model):
    _name = 'budget.approval'
    _description = "Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'ideatime.board.group']
    _order = "create_date desc"
    internal_user_id = fields.Many2one('res.users', index=True, tracking=True, default=lambda self: self.env.user)

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('budget.approval'))
    picking_ids = fields.One2many('stock.picking', 'budget_id', string='Pickings')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    wip_count = fields.Integer(string='WIP Orders', compute='_compute_picking_ids')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   help="Pricelist for current sales order.")
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, readonly=True, default='direct',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
        , help="If you deliver all products at once, the delivery order will be scheduled based on the greatest "
               "product lead time. Otherwise, it will be based on the shortest.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', required=True,
                                          help="Delivery address for current sales order.")
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=False,
        default=_default_warehouse_id)
    budget_template_id = fields.Many2one('budget.template')
    partA = fields.Boolean(string="Project Cost Estimate Part A")
    partB = fields.Boolean(string="Project Cost Estimate Part B")
    partC = fields.Boolean(string="General And Adminstrative Expense")
    ideatime_pic_info = fields.Boolean(string="Ideatime PIC Info")
    project_budget_plan = fields.Boolean(string="Project Budget Applicable Plan")
    batch = fields.Boolean(string="Budget Batch Line")
    project_id = fields.Many2one('project.project', required=True)

    name = fields.Char('Name', readonly=True, copy=False, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('project_check', 'Project Checking'),
        ('finance_check', 'Finance Checking'),
        ('approve', 'Approve'),
        ('close', 'Finance Checking'),
        ('done_close', 'Close'),
        ('cancel', 'Cancel')],
        string='State', required=True, readonly=True, default='draft', tracking=True)
    project_cost_estimate_part_id = fields.One2many('project.cost.estimate.line', 'approval_budget_id')
    project_cost_estimate_partc_id = fields.One2many('project.cost.estimate.partc', 'approval_budget_id')
    budget_line_id = fields.One2many('approval.budget.line', 'approval_budget_id')
    approval_budget_line_id = fields.One2many('approval.budget.order.line', 'approval_budget_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id.id)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", copy=False)
    partner_id = fields.Many2one('res.partner')
    user_id = fields.Many2one('res.users', index=True, tracking=True, default=lambda self: self.env.user)
    particular = fields.Char()
    description = fields.Text()
    partA_estimate_budget_total = fields.Float(readonly=True, compute="_compute_grand_total")
    partB_estimate_budget_total = fields.Float(readonly=True, compute="_compute_grand_total")
    start_date = fields.Date(string='Date')
    end_date = fields.Date(string="Due Date", widget="Date",
                           compute="_compute_due_date", store=True)
    no_of_day = fields.Char(compute="_compute_remaining_days", store=True)
    grand_total = fields.Float(compute="_compute_total", string="Grand Total")
    amount_total = fields.Float(compute="_compute_amount_total", string="Amount Total")
    self_purchase_cash_total = fields.Float(string="Self Purchase Cash Total", compute='_compute_partA_cost_total')
    self_purchase_credit_total = fields.Float(string="Self Purchase Credit Total", compute='_compute_partA_cost_total')
    self_purchase_total = fields.Float(string="Self Purchase Total", compute='_compute_partA_cost_total')
    pro_purchase_cash_total = fields.Float(string="Procurement Purchase Cash Total",
                                           compute='_compute_partA_cost_total')
    pro_purchase_credit_total = fields.Float(string="Procurement Purchase Credit Total",
                                             compute='_compute_partA_cost_total')
    pro_purchase_total = fields.Float(string="Procurement Purchase Total",
                                      compute='_compute_partA_cost_total')
    wip_manu_total = fields.Float(string="MFG Cost",
                                  compute='_compute_partA_cost_total')
    delivery_total = fields.Float(string="Delivery Total", compute='_compute_partA_cost_total')
    stock_total = fields.Float(string="Stock Total Cost", compute='_compute_partA_cost_total')
    # total_costs_id = fields.One2many('approval.budget.order.line', 'approval_budget_id')

    @api.onchange('partner_id')
    def _compute_partner_shippting_id(self):

        for record in self:
            if record.partner_id:
                record.partner_shipping_id = record.partner_id

    def action_budget_overview(self):
        pass

    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids), ('picking_type_id.code', '=', 'outgoing')]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action

    def action_view_wip(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids), ('picking_type_id.code', '=', 'internal')]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            get_delivery = order.picking_ids.search(
                [('picking_type_id.code', '=', 'outgoing'), ('budget_id', '=', self.id)])
            get_wip = order.picking_ids.search([('picking_type_id.code', '=', 'internal'), ('budget_id', '=', self.id)])
            order.delivery_count = len(get_delivery)
            order.wip_count = len(get_wip)

    def action_delivery_product(self):
        for order in self:
            for order_line in order.approval_budget_line_id:
                if (order_line.product_id):
                    order_line.order_line_parta_cost_ids.filtered(
                        lambda dir_line: dir_line.usage_type == 'deli')._action_launch_stock_rule()

        return

    def _prepare_wip_process(self):

        return {
            'picking_type_id': self.warehouse_id.int_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            # 'date': self.request_date,
            'origin': self.sale_order_id.name,
            'location_dest_id': self.warehouse_id.int_type_id.default_location_dest_id.id,
            'location_id': self.warehouse_id.int_type_id.default_location_src_id.id,
            'company_id': self.company_id.id,
            'project_id': self.project_id.id,
            'budget_id': self.id,
        }

    def action_manufacture_product(self):

        StockPicking = self.env['stock.picking']
        # for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
        for order in self:
            for order_line in order.approval_budget_line_id:
                if any(product.type in ['product', 'consu'] for product in
                       order_line.order_line_parta_cost_ids.filtered(
                           lambda dir_line: dir_line.usage_type == 'manu').product_id):
                    order = order.with_company(order.company_id)

                    res = order._prepare_wip_process()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    pickings = picking

                    moves = order.approval_budget_line_id.order_line_parta_cost_ids._create_stock_moves(picking)
                    moves = moves._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    # Get following pickings (created by push rules) to confirm them as well.
                    forward_pickings = self.env['stock.picking']._get_impacted_pickings(moves)
                    (pickings | forward_pickings).action_confirm()
                    picking.message_post_with_view('mail.message_origin_link',
                                                   values={'self': picking, 'origin': order},
                                                   subtype_id=self.env.ref('mail.mt_note').id)
                # order.write({'state': 'assigned'})
        return self

    @api.onchange('budget_template_id')
    def onchange_template(self):
        for rec in self:
            for template in rec.budget_template_id:
                rec.partA = template.partA
                rec.partB = template.partB
                rec.partC = template.partC
                rec.project_budget_plan = template.project_budget_plan
                rec.batch = template.batch

    @api.depends('approval_budget_line_id')
    def _compute_partA_cost_total(self):
        self.delivery_total = 0
        self.self_purchase_cash_total = 0
        self.self_purchase_credit_total = 0
        self.self_purchase_total = 0
        self.pro_purchase_cash_total = 0
        self.pro_purchase_credit_total = 0
        self.pro_purchase_total = 0
        self.wip_manu_total = 0
        self.stock_total = 0
        for record in self.approval_budget_line_id:
            for direct_line in record.order_line_parta_cost_ids:
                if direct_line.usage_type == 'self' and direct_line.payment_type == 'cash':
                    self.self_purchase_cash_total += direct_line.total_amount
                elif direct_line.usage_type == 'self' and direct_line.payment_type == 'credit':
                    self.self_purchase_credit_total += direct_line.total_amount
                elif direct_line.usage_type == 'proc' and direct_line.payment_type == 'cash':
                    self.pro_purchase_cash_total += direct_line.total_amount
                elif direct_line.usage_type == 'proc' and direct_line.payment_type == 'credit':
                    self.pro_purchase_credit_total += direct_line.total_amount
                elif direct_line.usage_type == 'deli':
                    self.delivery_total += direct_line.total_amount
                elif direct_line.usage_type == 'manu':
                    self.wip_manu_total += direct_line.total_amount
                self.self_purchase_total = self.self_purchase_cash_total + self.self_purchase_credit_total
                self.pro_purchase_total = self.pro_purchase_cash_total + self.pro_purchase_credit_total
                self.stock_total = self.wip_manu_total + self.delivery_total

    @api.depends('budget_line_id')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = 0.0
            for line in rec.budget_line_id:
                rec.amount_total += line.amount

    @api.onchange('project_id')
    def set_customer_name(self):
        for rec in self:
            if rec.project_id:
                rec.partner_id = rec.project_id.partner_id

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res = super(BudgetApproval, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                     orderby=orderby, lazy=lazy)
        budget = self.env['budget.approval']
        for line in res:
            if '__domain' in line:
                budget = self.search(line['__domain'])
            if 'grand_total' in fields:
                line['grand_total'] = sum(budget.mapped('grand_total'))
        return res

    @api.onchange('partA_estimate_budget_total', 'partB_estimate_budget_total')
    def _compute_total(self):
        for line in self:
            line.grand_total = 0
            if line.partA_estimate_budget_total:
                line.grand_total += line.partA_estimate_budget_total
            if line.partB_estimate_budget_total:
                line.grand_total += line.partB_estimate_budget_total

    @api.depends('start_date', 'end_date')
    def _compute_remaining_days(self):
        for record in self:
            if record.start_date and record.end_date:
                record.no_of_day = str((record.end_date - record.start_date).days)

    @api.depends('no_of_day', 'start_date')
    def _compute_due_date(self):
        for record in self:
            if record.no_of_day and record.start_date:
                start_date = fields.Datetime.from_string(record.start_date)
                delta = timedelta(days=int(record.no_of_day))
                end_date_datetime = start_date + delta
                record.end_date = end_date_datetime.date()

    @api.depends('approval_budget_line_id', 'project_cost_estimate_part_id')
    def _compute_grand_total(self):
        for line in self:
            line.partA_estimate_budget_total = 0
            line.partB_estimate_budget_total = 0
            for budget_line in line.approval_budget_line_id:
                line.partA_estimate_budget_total += budget_line.cost_estimate
            for expense_line in line.project_cost_estimate_part_id:
                line.partB_estimate_budget_total += expense_line.cost_estimate

    def compute_project_cost_estimate(self):
        summary_line = []

        for line in self.project_cost_estimate_part_id:
            if line.display_type:
                summary_line.append({
                    'name': line.name,
                    'qty': 0,
                    'unit': '',
                    'unit_price': 0,
                    'subtotal': 0
                })
            else:
                if summary_line:
                    summary_line[-1]['qty'] += line.product_uom_qty
                    summary_line[-1]['unit'] = line.product_uom_label or ''
                    summary_line[-1]['unit_price'] += line.price_unit
                    summary_line[-1]['subtotal'] += line.price_subtotal

        return summary_line

    def add_sale_order_line(self):
        if self.sale_order_id:
            template = self.sale_order_id
            self.partner_id = template.partner_id
            budget_line_obj = self.env['approval.budget.order.line']
            for line in template.order_line:
                if self.approval_budget_line_id:
                    found = False
                    for budget_line in self.approval_budget_line_id:
                        if budget_line.sale_order_line_id == line.id:
                            found = True
                            break
                    if found:
                        continue
                # if line.id in self.approval_budget_line_id.sale_order_line_id:
                #     return False
                budget_line = budget_line_obj.create({
                    'sale_order_line_id': line.id,
                    'approval_budget_id': self.id,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_subtotal': line.price_subtotal,
                    'remark': line.remark,
                    'display_type': line.display_type,

                })

                direct_line_obj = self.env['budget.parta.cost']
                for parta in budget_line:
                    get_bom = self.env['mrp.bom.line'].search([
                        ('bom_id.product_id', '=', parta.product_id.id),
                        ('bom_id.product_qty', '=', 1.00)
                    ])
                    for bom_line in get_bom:
                        direct_line_obj.create({'product_id': bom_line.product_id.id,
                                                # 'pcs': budget_line.pcs,
                                                'qty': parta.product_uom_qty * bom_line.product_qty,
                                                # 'height': budget_line.height,
                                                'product_uom': bom_line.product_uom_id.id,
                                                # 'price unit': budget.line.price_unit,
                                                'cost_type_id': bom_line.product_id.cost_type_id.ids[0],
                                                'budget_order_line_id': parta.id
                                                })

                item_confirm_line_obj = self.env['budget.order.confirm.line']
                for item_confirm_line in line.item_order_confirm_ids:
                    item_confirm_line_obj.create({
                        'particular_id': item_confirm_line.particular_id,
                        'description': item_confirm_line.description,
                        'budget_order_line_id': budget_line.id
                    })
                client_demand_line_obj = self.env['budget.client.demand.line']
                for client_demand_line in line.client_demand_ids:
                    client_demand_line_obj.create({
                        'particular_id': client_demand_line.particular_id,
                        'description': client_demand_line.description,
                        'budget_order_line_id': budget_line.id
                    })

    def action_submit(self):
        if self.state == 'draft':
            self.write({'state': 'submit'})

    def action_project_check(self):
        if self.state == 'submit':
            self.write({'state': 'project_check'})

    def action_finance_check(self):
        if self.state == 'project_check':
            self.write({'state': 'finance_check'})

    def action_approve(self):
        if self.state == 'finance_check':
            self.write({'state': 'approve'})
        else:
            self.write({'state': 'done_close'})

    def action_close(self):

        if self.state in ('approve', 'done'):
            self.write({'state': 'done_close'})
        else:
            self.write({'state': 'close'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_finance_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft(self):
        if self.state == 'cancel':
            self.write({'state': 'draft'})

    def action_set_to_finance_check(self):
        self.write({'state': 'finance_check'})

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a budget. You must first cancel it.'))
        return super(BudgetApproval, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('budget.approval') or 'New'
        result = super(BudgetApproval, self).create(vals)
        result._add_board_users_to_allowed_uids()
        return result

    def write(self, vals):
        res = super(BudgetApproval, self).write(vals)
        self._add_board_users_to_allowed_uids()
        if self.env.user not in self.allowed_user_ids:
            self.allowed_user_ids |= self.env.user
        return res

    project_cost_estimate_file = fields.Binary(string='Project Cost Estimate File')
    project_estimate_anlaysis_file = fields.Binary(string="Project Cost Estimate Analysis")

    def get_budget_order_line(self):
        cost_estimate_array = []

        direct_material_cost = {'sr': '1', 'name': 'Direct material cost', 'data': []}
        indirect_material_cost = {'sr': '2', 'name': 'Indirect material cost', 'data': []}
        direct_labour_cost = {'sr': '3', 'name': 'Direct labour cost', 'data': []}
        thirdparty_contractor_cost = {'sr': '4', 'name': 'Thirdparty cost (Contractor)', 'data': []}
        thirdparty_subcontractor_cost = {'sr': '5', 'name': 'Thirdparty cost (Subcontractor)', 'data': []}

        get_direct_material = self.env['budget.parta.cost'].search(
            [('budget_order_line_id', 'in', self.approval_budget_line_id.ids)])

        to_group_array = {
            'direct_material_cost': get_direct_material
        }

        for key, value in to_group_array.items():
            item_no = 1
            group_by_product = {}
            for k, g in groupby(value, lambda x: x.product_id):
                if k in group_by_product:
                    group_by_product[k].extend(list(g))
                else:
                    group_by_product[k] = list(g)
            # group_by_product = {k:list(g) for k, g in groupby(value, lambda x: x.product_id)}
            print(group_by_product)
            for item_key, item_value in group_by_product.items():
                data_dict = {
                    'no': item_no,
                    'item_name': item_key.name,
                    'item_code': item_key.barcode
                }
                for attr_val in item_key.product_template_attribute_value_ids:
                    data_dict['item_name'] += ' ' + attr_val.name
                total_qty = 0
                unit_price = 0
                unit = ''
                for grouped_product in item_value:
                    total_qty += grouped_product.product_uom_qty
                    uom = grouped_product.product_uom.name or ''
                    unit_price = grouped_product.unit_price
                data_dict['qty'] = total_qty
                data_dict['unit'] = uom
                data_dict['price'] = unit_price
                data_dict['total_amount'] = total_qty * unit_price

                eval(key)['data'].append(data_dict)
                item_no += 1

        cost_estimate_array.append(direct_material_cost)
        cost_estimate_array.append(indirect_material_cost)
        cost_estimate_array.append(direct_labour_cost)
        cost_estimate_array.append(thirdparty_contractor_cost)
        cost_estimate_array.append(thirdparty_subcontractor_cost)

        return cost_estimate_array


class ApprovalBudgetLine(models.Model):
    _name = 'approval.budget.line'
    _description = 'Approval Budget Line'

    name = fields.Char(string="Batch No", compute="_batch_sequence")
    branch_des_id = fields.Many2one('branch.description')

    description = fields.Many2one('product.product', string="Description")
    amount = fields.Integer(string="Amount", compute='_compute_amount')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.currency_id.id)
    applicable_date = fields.Date(string="Applicable date", default=fields.Date.today())
    complete_date = fields.Date(string="Complete date", default=fields.Date.today())
    remark = fields.Text(string="Remark")
    project_budget_id = fields.Many2one('project.project', string="PBAP ID")
    approval_budget_id = fields.Many2one('budget.approval', ondelete='cascade')
    cash_paid = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done')
    ], string="Cash Paid", default="pending")
    state = fields.Selection(string='State', required=True, readonly=True, tracking=True,
                             related="approval_budget_id.state")
    batch_budget_line = fields.One2many('budget.batch.line', 'batch_id', string="Batch Budget Line")

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    @api.depends('approval_budget_id.budget_line_id')
    def _batch_sequence(self):
        for line in self:
            batch_name = 'BATCH'
            no = 0
            for l in line.approval_budget_id.budget_line_id:
                no += 1
                l.name = batch_name + str(no)

    def _compute_amount(self):
        for rec in self:
            rec.amount = 0
            batch_obj = rec.env['budget.batch.line'].search(
                [('budget_id', 'in', rec.approval_budget_id.ids), ('batch_id', '=', rec.id)])
            for line in batch_obj:
                rec.amount += line.total_amount


class BudgetBatch(models.Model):
    _name = 'budget.batch.line'
    _description = 'Budget Batch Line'

    budget_partB_id = fields.Many2one('project.cost.estimate.line')
    budget_partC_id = fields.Many2one('project.cost.estimate.partc')

    budget_parta_cost_id = fields.Many2one('budget.parta.cost')

    budget_id = fields.Many2one('budget.approval', required=True)

    batch_id = fields.Many2one('approval.budget.line', domain="[('approval_budget_id', '=',budget_id)]")
    product_uom_qty = fields.Float(string="Qty", digits='Product Unit of Measure', required=True,
                                   default=0.0)
    unit_price = fields.Float(string="Price", digits='Product Unit of Measure',
                              compute='_compute_product_and_total')
    total_amount = fields.Float(string='Total Amount', compute='_compute_product_and_total')
    product_id = fields.Many2one('product.product', compute='_compute_product_and_total')
    usage_type = fields.Selection(
        [('self', 'Self Purchase'), ('proc', 'Procurement Purchase'), ('deli', 'Stock Delivery')], 'Type',
        compute='_compute_check_po')
    unit = fields.Many2one('uom.uom', string='Unit', compute='_compute_product_and_total')

    def _compute_check_po(self):
        for rec in self:
            for dir_line in rec.budget_parta_cost_id:
                rec.usage_type = dir_line.usage_type
            for partB_line in rec.budget_partB_id:
                rec.usage_type = partB_line.usage_type
            for partC_line in rec.budget_partC_id:
                rec.usage_type = partC_line.usage_type

    @api.onchange('unit_price', 'product_uom_qty')
    def _compute_product_and_total(self):
        for rec in self:
            rec.total_amount = 0
            for dir_line in rec.budget_parta_cost_id:
                rec.product_id = dir_line.product_id.id
                rec.unit_price = dir_line.unit_price
                rec.unit = dir_line.product_uom
                rec.total_amount = rec.product_uom_qty * rec.unit_price
            for partB_line in rec.budget_partB_id:
                rec.product_id = partB_line.product_id.id
                rec.unit_price = partB_line.price_unit
                rec.unit = partB_line.product_uom
                rec.total_amount = rec.unit_price * rec.product_uom_qty
            for partC_line in rec.budget_partC_id:
                rec.product_id = partC_line.product_id.id
                rec.unit_price = partC_line.price_unit
                rec.unit = partC_line.product_uom
                rec.total_amount = rec.unit_price * rec.product_uom_qty

    def write(self, vals):
        template = super(BudgetBatch, self).write(vals)
        for rec in self:
            if rec.budget_parta_cost_id:
                if rec.product_uom_qty > rec.budget_parta_cost_id.qty:
                    raise UserError(_('Plz check! Product Quantity'))
            return template


class BugetItemOrderConfirmation(models.Model):
    _name = 'budget.order.confirm.line'
    _description = 'Budget Order Confirmation Line'

    particular_id = fields.Char(string='Particular')
    description = fields.Text('Description')
    budget_order_line_id = fields.Many2one('approval.budget.order.line')


class BudgetClientDemand(models.Model):
    _name = 'budget.client.demand.line'
    _description = 'Budget Client Demand Line'

    particular_id = fields.Char(string='Particular')
    description = fields.Text('Description')
    budget_order_line_id = fields.Many2one('approval.budget.order.line')


class BudgetCalculatorLine(models.Model):
    _name = 'budget.calculator.line'
    _description = 'Budget Calculator Line'

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
    parta_cost_line_id = fields.Many2one('budget.parta.cost')

    project_cost_estimate_line_id = fields.Many2one('project.cost.estimate.line')
    project_cost_estimate_partc_id = fields.Many2one('project.cost.estimate.partc')
    product_uom = fields.Char(string='UOM', related="parta_cost_line_id.product_uom.name")

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)
