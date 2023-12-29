from itertools import groupby

from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare


class ProcessRemark(models.Model):
    _name = 'process.remark.line'
    _description = 'Process Remark'

    particular_id = fields.Char()
    description = fields.Text()
    project_process_id = fields.Many2one('project.project')


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    def open_project_expense_claim(self):
        tree_view_id = self.env.ref('ideatime_budget.project_expense_claim_tree').id
        form_view_id = self.env.ref('ideatime_budget.project_expense_claim_form').id
        return {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Project expense claim'),
            'res_model': 'project.expense.claim',
            'domain': "[('project_id', '=', active_id)]",
            'context': {'default_project_id': self.id}

        }

    def map_tasks(self, new_project_id):
        """ copy and map tasks from old to new project """
        tasks = self.env['project.task']
        # We want to copy archived task, but do not propagate an active_test context key
        task_ids = self.env['project.task'].with_context(active_test=False).search([('project_id', '=', self.id)],
                                                                                   order='parent_id').ids
        old_to_new_tasks = {}
        for task in self.env['project.task'].browse(task_ids):
            # preserve task name and stage, normally altered during copy
            defaults = self._map_tasks_default_valeus(task)
            if task.parent_id:
                # set the parent to the duplicated task
                defaults['parent_id'] = old_to_new_tasks.get(task.parent_id.id, False)
            new_task = task.copy(defaults)
            old_to_new_tasks[task.id] = new_task.id
            tasks += new_task

        return self.write({'tasks': [(6, 0, tasks.ids)]})

    def open_quotation(self):
        tree_view_id = self.env.ref('sale.view_quotation_tree').id
        form_view_id = self.env.ref('sale.view_order_form').id
        return {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'form',
            'name': _('Quotations'),
            'res_model': 'sale.order',
            'domain': "[('project_id', '=', active_id)]",
            'context': {'default_project_id': self.id}
        }

    def open_budget_approval(self):
        tree_view_id = self.env.ref('ideatime_project.list').id
        form_view_id = self.env.ref('ideatime_project.form').id
        return {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'form',
            'name': _('Budgets'),
            'res_model': 'budget.approval',
            'domain': "[('project_id', '=', active_id)]",
            'context': {'default_project_id': self.id}
        }

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    def checklist_progress(self):
        """:return the value for the check list progress"""
        task_obj = self.env['project.task']
        for record in self:
            record.checklist_progress = 0
            total_task = 0
            total_done = 0
            get_task = task_obj.search([('project_id', '=', record.id)])
            for task in get_task:
                if not task.parent_id and task.stage_id.stage_state != 'cancel':
                    total_task += 1
                    if task.stage_id.stage_state == 'done':
                        total_done += 1

            if total_task != 0:
                record.checklist_progress = (total_done * 100) / total_task

    def _compute_task_count(self):
        task_data = self.env['project.task'].read_group(
            [('parent_id', '=', False), ('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False),
             ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count = result.get(project.id, 0)

    @api.onchange('cate_group_id', 'cate_sector_id', 'cate_line_id', 'cate_particular_id', 'cate_function_id',
                  'cate_option_id')
    def _compute_product(self):
        product_obj = self.env['product.product']
        query = [('is_material', '=', True)]
        if self.cate_group_id:
            query.append(('cate_group_id', '=', self.cate_group_id.id))
        if self.cate_sector_id:
            query.append(('cate_sector_id', '=', self.cate_sector_id.id))

        search_product = product_obj.search(query)
        self.selectable_product_ids = search_product

    material_line_ids = fields.One2many('used.material.line', 'project_id', string='Material Line')
    variable_line_ids = fields.One2many('variable.manu.overhead', 'project_id', string='Variable Line')
    sale_ids = fields.One2many('sale.order', 'project_id')
    sale_number = fields.Integer(compute='_compute_count', string="Number of Quotations")
    meeting_ids = fields.One2many('calendar.event', 'project_id', string='Meetings', copy=False)
    meeting_count = fields.Integer("# Meetings", compute='_compute_meeting_count')
    employee_id = fields.Many2many('hr.employee', string="Employee")

    income = fields.Float('Income', compute='_compute_total_count')
    expense = fields.Float('Expense', compute='_compute_total_count')
    profit = fields.Float('Profit', compute='_compute_total_count')

    cate_group_id = fields.Many2one('service.category.group', string='Service Group')

    cate_particular_id = fields.Many2one('service.category.particular', string='Particular')
    cate_function_id = fields.Many2one('service.category.function', string='Function')
    cate_option_id = fields.Many2one('service.category.option', string='Option')

    selectable_product_ids = fields.Many2many('product.product', compute="_compute_product")

    direct_labour_cost = fields.Float('Direct Labour Cost')
    elect_expense = fields.Float('Electrical Expense')
    packaging_cost = fields.Float('Packaging Cost')
    third_party_install_fees = fields.Float('Third Party Fees')
    risk_percent = fields.Float('Risk %')

    rental_fees = fields.Float('Rental Fees')
    machine_insurance = fields.Float('Machine Insurance')
    building_deprecration = fields.Float('Building Deprecration')
    machine_deprecration = fields.Float('Machine Deprecration')
    transport_fees = fields.Float('Transpotation Fees')
    delivery_cost = fields.Float('Delivery Cost')
    manu_overhead = fields.Float('Manufacturing Overhead')
    other_expense = fields.Float('Other Expenses')

    admin_expense = fields.Float('Admin Expenses')
    selling_expense = fields.Float('Selling Expense')
    finance_expense = fields.Float('Finance Expense')
    project_expense = fields.Float('Project Expense')
    procurement_expense = fields.Float('Procurement Expense')

    calculation = fields.Float('Calculation')

    in_ex_ids = fields.One2many('idea.income.expense', 'project_id')
    action_plan_ids = fields.One2many('action.plan', 'project_id', string='Action Plan')

    project_name = fields.Char(compute="_compute_project_name")

    priority = fields.Selection([
        ('0', 'Start'),
        ('1', 'Bad'),
        ('2', 'Normal'),
        ('3', 'Good'),
        ('4', 'Excellent'),
    ], default='0', index=True, string="Priority")

    initial_feedback_ids = fields.One2many('initial.feedback.process', 'project_id')
    street = fields.Char('Street')
    ward = fields.Char('Ward')
    land_number = fields.Char('No.')
    site_name = fields.Char('Site name / Building name')
    tower_type = fields.Char('Building Type')
    tower_no = fields.Char('Building No')
    floor = fields.Char('Floor')
    country_id = fields.Many2one('res.country')
    region = fields.Many2one('customer.region', string='Region')
    city = fields.Many2one('customer.city', string='City')
    township = fields.Many2one('customer.township', string='Township')
    bd_senior_management_id = fields.Many2one('res.users', string="BD Senior management ", tracking=True)
    warehouse_senior_management_id = fields.Many2one('res.users', tracking=True)
    order_agreement_confirm_pic = fields.Many2one('res.users', tracking=True)
    project_implement_approve_pic = fields.Many2one('res.users', tracking=True)
    quotation_pic = fields.Many2one('res.users', tracking=True)
    order_agreement_pic = fields.Many2one('res.users', tracking=True)
    quot_senior_pic = fields.Many2one('res.partner', string="Senior PIC", tracking=True)
    order_agreement_senior_pic = fields.Many2one('res.partner', string="Senior PIC", tracking=True)
    client_pic_ids = fields.One2many('client.pic', 'project_client_pic_id')
    internal_pic_ids = fields.One2many('internal.pic', 'project_internal_pic_id')
    supplier_pic_ids = fields.One2many('supplier.pic', 'project_supplier_pic_id')
    internal_user_id = fields.Many2many('res.users', tracking=True)
    process_remark_line = fields.One2many('process.remark.line', 'project_process_id')
    due_date = fields.Date(string="Due Date")
    project_budget_line = fields.One2many('project.budget.line', 'project_budget_id')
    project_cost_estimate_line = fields.One2many('project.expense.order.line', 'project_cost_estimate_id')
    project_order_line = fields.One2many('project.order.line', 'order_id')
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
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address',
                                          help="Delivery address for current sales order.")
    project_user_type = fields.Selection([
        ('sale', 'Sale Order Project'),
        ('internal', 'Internal Project')
    ], string='Project User Type', required=True, default="sale")
    responsible_user = fields.Many2one('res.users', string="Responsible User")
    internal_delivery_id = fields.Many2one('res.users', string='Delivery Address',
                                           help="Delivery address for internal user.")
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True,
        default=_default_warehouse_id)
    expense_total_amount = fields.Monetary(string='Total Amount', compute="_compute_expense_total_amount")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   tracking=True)
    project_cost_estimate_file = fields.Binary(string='Project Cost Estimate File')
    project_estimate_anlaysis_file = fields.Binary(string="Project Cost Estimate Analysis")
    file_name = fields.Char(string="File Name")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('order_agreement', 'Order Agreegment Confirm'),
        ('budget', 'Budget Available'),
        ('check', 'Detail Check'),
        ('approve', 'Project Implement Approve'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='draft')
    budget_user_id = fields.Many2one('res.users', string='Approve Budget User', tracking=True)
    budget_date_time = fields.Datetime(string='Approve Order Budget Date', tracking=True)
    project_senior_approve = fields.Boolean(default=False, compute="_compute_project_senior_approve")
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    estimate_file_confirm = fields.Boolean(compute="_compute_project_cost_estimate_confirm")
    check_user_id = fields.Many2one('res.users', string='Check User', tracking=True)
    check_date_time = fields.Datetime(string='Check Date', tracking=True)
    finance_approve = fields.Boolean(default=False, compute="_compute_finance_approve")
    approve_user_id = fields.Many2one('res.users', string='Approve Purchase User', tracking=True)
    approve_date_time = fields.Datetime(string='Approve Purchase Date', tracking=True)
    project_director_approve = fields.Boolean(default="False", compute="_compute_project_director_approve")
    start_date = fields.Date()
    end_date = fields.Date()
    no_of_day = fields.Char(compute="_compute_remaining_days", store=True)

    actionstep_template_id = fields.Many2one('actionstep.template')
    create_task_confirm = fields.Boolean()

    budget_approval_ids = fields.One2many('budget.approval', 'project_id', string="Budget")
    budget_approval_count = fields.Integer(compute="_compute_count")

    decoration_survey_count = fields.Integer(compute='_compute_decoration_survey_count', string="Survey Count")
    decoration_survey_ids = fields.One2many('ideatime.task.survey', 'project_id', string='Survey')
    jo_accept_count = fields.Integer(compute="_compute_jo_count", string="JO Count")
    jo_accept_ids = fields.One2many('jo.acceptance', 'project_id', string='Jo Accept')
    design_proposal_count = fields.Integer(compute="_compute_design_count", string="Design Proposal")
    design_proposal_ids = fields.One2many('design.proposal', 'project_id', string='Design Proposal')

    particular = fields.Char()
    description = fields.Text()
    is_template = fields.Boolean(string='Is Template Project', default=False)
    survey_count = fields.Integer(compute='_compute_survey_count', string="Survey Count")
    survey_ids = fields.One2many('ideatime.survey', 'project_survey_id', string='Survey')
    checklist_progress = fields.Float(compute=checklist_progress, string='Progress', recompute=True,
                                      default=0.0)
    max_rate = fields.Integer(string='Maximum rate', default=100)

    @api.depends('design_proposal_ids')
    def _compute_design_count(self):
        for task in self:
            task.design_proposal_count = len(task.design_proposal_ids)

    @api.depends('jo_accept_ids')
    def _compute_jo_count(self):
        for task in self:
            task.jo_accept_count = len(task.jo_accept_ids)

    @api.depends('decoration_survey_ids')
    def _compute_decoration_survey_count(self):
        for task in self:
            task.decoration_survey_count = len(task.decoration_survey_ids)

    @api.onchange('country_id')
    def set_region_to(self):
        for rec in self:
            if rec.country_id:
                ids = self.env['customer.region'].search([('country_id', '=', rec.country_id.id)])
                return {
                    'domain': {'region': [('id', 'in', ids.ids)], }
                }

    @api.onchange('region')
    def set_city_to(self):
        for rec in self:
            rec.country_id = rec.region.country_id
            if rec.region:
                ids = self.env['customer.city'].search([('region', '=', rec.region.id)])
                return {
                    'domain': {'city': [('id', 'in', ids.ids)], }
                }

    @api.onchange('city')
    def set_township_to(self):
        for rec in self:
            rec.region = rec.city.region
            if rec.city:
                ids = self.env['customer.township'].search([('city', '=', rec.city.id)])
                return {
                    'domain': {'township': [('id', 'in', ids.ids)], }
                }

    @api.onchange('township')
    def _set_city_region(self):
        for rec in self:
            rec.city = rec.township.city

    @api.onchange('actionstep_template_id')
    def onchange_actionstep_template_id(self):
        self.action_plan_ids = False
        template = self.actionstep_template_id.with_context(lang=self.partner_id.lang)
        order_lines = []
        for line in template.actionstep_line_id:
            order_line = {'name': line.name, 'actionstep_task': []}
            for task_line in line.actionstep_task_id:
                order_line['actionstep_task'].append((4, task_line.id))
            order_lines.append(order_line)
        self.action_plan_ids = order_lines

    @api.onchange('cate_group_id')
    def set_service_sector_to(self):
        self.cate_sector_id = False
        if self.cate_group_id:
            ids = self.env['service.category.sector'].search([('left_id', '=', self.cate_group_id.id)])
            return {
                'domain': {'cate_sector_id': [('id', 'in', ids.ids)], }
            }

    @api.onchange('cate_sector_id')
    def set_service_line_to(self):
        self.cate_line_id = False
        if self.cate_sector_id:
            ids = self.env['service.category.line'].search([('left_id', '=', self.cate_sector_id.id)])
            return {
                'domain': {'cate_line_id': [('id', 'in', ids.ids)], }
            }

    @api.depends('start_date', 'end_date')
    def _compute_remaining_days(self):
        for record in self:
            if record.start_date and record.end_date:
                record.no_of_day = str((record.end_date - record.start_date).days)

    @api.depends('director')
    def _compute_project_director_approve(self):
        for record in self:
            record.project_director_approve = False
            if record.director == record.current_user:
                record.project_director_approve = True

    def action_approve(self):
        if self.filtered(lambda proj: proj.state not in ('draft', 'budget', 'check')):
            raise UserError(_("Project must be detail check state in order to Approve Quotation."))
        self.write(
            {'state': 'approve', 'approve_user_id': self.env.user.id, 'approve_date_time': fields.Datetime.now()})
        return

    @api.depends('finance_senior_management_id')
    def _compute_finance_approve(self):
        for record in self:
            record.finance_approve = False
            if record.finance_senior_management_id == record.current_user:
                record.finance_approve = True

    def action_detail_check(self):
        if self.filtered(lambda proj: proj.state not in ('draft', 'budget')):
            raise UserError(_("Project Waiting state in order to Approve Quotation."))
        self.write({'state': 'check', 'check_user_id': self.env.user.id, 'check_date_time': fields.Datetime.now()})
        return

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
        self.update({'current_user': self.env.user.id})

    @api.depends('project_senior_management_id')
    def _compute_project_senior_approve(self):
        for record in self:
            record.project_senior_approve = False
            if record.project_senior_management_id == record.current_user:
                record.project_senior_approve = True

    @api.depends('project_cost_estimate_file', 'project_estimate_anlaysis_file')
    def _compute_project_cost_estimate_confirm(self):
        self.estimate_file_confirm = False
        if self.project_cost_estimate_file and self.project_estimate_anlaysis_file:
            self.estimate_file_confirm = True

    def action_budget(self):
        if self.filtered(lambda proj: proj.state not in ('draft')):
            raise UserError(_("Project Waiting state in order to Approve Project Budget."))
        self.write({'state': 'budget', 'budget_user_id': self.env.user.id, 'budget_date_time': fields.Datetime.now()})
        return

    @api.depends('project_order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.project_order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('project_cost_estimate_line.price_subtotal')
    def _compute_expense_total_amount(self):
        for expense in self:
            expense_total = 0
            for total_expense_line in self.project_cost_estimate_line:
                if self.project_cost_estimate_line:
                    expense_total += total_expense_line.price_subtotal
            expense.update({
                'expense_total_amount': expense_total,
            })

    @api.onchange('partner_id')
    def _compute_partner_shipping_id(self):
        for record in self:
            if record.partner_id:
                record.partner_shipping_id = record.partner_id

    @api.onchange('responsible_user')
    def _compute_internal_delivery_id(self):
        for record in self:
            if record.responsible_user:
                record.internal_delivery_id = record.responsible_user

    def action_view_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        return action

    def action_delivery_direct_mat_product(self):
        for order in self:
            for order_line in order.project_order_line:
                if (order_line.product_id):
                    order_line.order_line_parta_cost_ids._action_launch_stock_rule()

        return

    @api.onchange('country_id', 'region', 'city', 'township', 'street', 'ward', 'land_number', 'site_name',
                  'tower_type', 'tower_no', 'floor')
    def _compute_material_code_name(self):

        project_site = [[lambda: '', lambda: '(' + self.site_name + ')'][self.site_name != False](), ' ',
                        self.tower_type or '', ' ', self.tower_no or '', ' ', self.floor or '',
                        [lambda: '', lambda: ',No.:' + self.land_number][self.land_number != False](),
                        self.street or '', ' ', self.ward or '', ' ', self.township.name or '']
        region_list = [self.city.name or '', self.region.name or '', self.country_id.name or '']
        self.project_site = "".join(str(site) for site in filter(lambda r: r != '', project_site)) + ' ' + ", ".join(
            str(region) for region in filter(lambda r: r != '', region_list))

    def _compute_meeting_count(self):
        for project in self:
            project.meeting_count = len(project.meeting_ids)

    def create_quotation(self):
        if not self.partner_id:
            raise UserError(_('Need Customer'))

        if self.material_line_ids:
            create_quo = self.env['sale.order'].create({'partner_id': self.partner_id.id,
                                                        'project_id': self.id})
            so_line_obj = self.env['sale.order.line']
        for line in self.material_line_ids:
            so_line_obj.create({'product_id': line.product_id.id,
                                'name': line.name,
                                'product_uom_qty': line.product_uom_qty,
                                'price_unit': line.price_unit,
                                'order_id': create_quo.id,
                                })

    def _compute_survey_count(self):
        for survey in self:
            count = 0
            if survey.survey_ids:
                count += 1
                survey.survey_count = count

    def _compute_count(self):
        for order in self:
            order.sale_number = len(order.sale_ids)
            order.budget_approval_count = len(order.budget_approval_ids)

    @api.depends('material_line_ids', 'variable_line_ids', 'sale_ids', 'direct_labour_cost', 'elect_expense',
                 'packaging_cost', 'third_party_install_fees', 'risk_percent', 'rental_fees', 'machine_insurance',
                 'building_deprecration', 'machine_deprecration', 'transport_fees', 'delivery_cost', 'manu_overhead',
                 'other_expense', 'admin_expense', 'selling_expense', 'finance_expense', 'project_expense',
                 'procurement_expense')
    def _compute_total_count(self):
        for lead in self:
            income = 0.0
            expense = 0.0
            for sale_order in lead.sale_ids:
                for invoice in sale_order.invoice_ids:
                    if invoice.move_type == 'out_invoice' and invoice.state == 'posted':
                        income += invoice.amount_total_signed

            exp_vouchers = self.env['expense.voucher'].search([('project_ids', 'in', (lead.id))])
            for exp_vou in exp_vouchers:
                expense += exp_vou.amount_total / len(exp_vou.project_ids)
            lead.update({
                'income': income,
                'expense': expense,
                'profit': income - expense,
            })

    @api.model
    def create(self, vals):
        project_stages = self.env['project.task.type']
        if vals.get('proj_type_id'):
            project_type = self.env['project.type'].browse(vals.get('proj_type_id'))
            project_stages = self.env['project.task.type'].search(
                [('project_ids', 'in', project_type.template_project_id.id)])
            seq = self.env['ir.sequence'].browse(project_type.sequence_id.id)
            if seq:
                vals['name'] = seq.next_by_id()

        res = super(Project, self).create(vals)
        if vals.get('proj_type_id'):
            if project_stages and len(project_stages) > 0:
                for stage in project_stages:
                    stage.project_ids = [(4, res.id, res.id)]  # (4, res.id)

            if project_type.template_project_id:
                proj_task_obj = self.env['project.task']
                search_template_task = proj_task_obj.search([('project_id', '=', project_type.template_project_id.id)],
                                                            order='parent_id')
                old_new_tasks_ids = {}
                for task_under_proj in search_template_task:
                    task_create_dict = {
                        'name': task_under_proj.name,
                        'description': task_under_proj.description,
                        'project_id': res.id
                    }

                    if task_under_proj.parent_id:
                        task_create_dict['parent_id'] = old_new_tasks_ids[task_under_proj.parent_id.id]

                    create_task = proj_task_obj.create(task_create_dict)
                    old_new_tasks_ids[task_under_proj.id] = create_task.id

        return res

    def open_projects(self):
        ctx = dict(self._context)
        action = self.env['ir.actions.act_window'].for_xml_id('ideatime_project', 'act_project_project')
        return dict(action, context=ctx)

    def action_view_in_ex(self):
        action = self.env.ref('ideatime_project.action_idea_in_ex')

        action['domain'] = {'project_id': self.id}
        result = action.read()[0]
        result['context'] = {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'}
        res = self.env.ref('ideatime_project.idea_in_ex_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.in_ex_ids.id
        return result

    def _compute_project_name(self):
        for record in self:
            service_project_name = []
            if record.cate_sector_id:
                service_project_name.append(str(record.cate_sector_id.name))
            if record.cate_line_id:
                service_project_name.append(str(record.cate_line_id.name))

            if record.manual_project_name:
                service_project_name.append(str(record.manual_project_name))
            record.project_name = " ".join(str(x) for x in service_project_name)

    create_task_invisible = fields.Boolean(default=False)

    def action_surveyinfo(self, context={}):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'ideatime_project.report_project_task_survey',
            'model': 'project.project',
            'report_type': "qweb-html",
            'name': 'Decoration Survey info'
        }

    def create_tasks(self):
        self.create_task_invisible = False
        self.create_task_confirm = True

        action_plan_lines = self.env['action.plan'].search([('project_id', '=', self.id)])
        for line in action_plan_lines:
            for task_line in line.actionstep_task:
                self.env['project.task'].create({
                    'name': task_line.name,
                    'action_step_id': line.id,
                    'project_id': self.id,
                    'stage_id': 4
                })

    @api.onchange('action_plan_ids')
    def check_create_task(self):
        print("Check Create Task")
        self.create_task_invisible = True
        # self.create_task_confirm = True

    def get_sale_order_line(self):
        cost_estimate_array = []

        direct_material_cost = {'sr': '1', 'name': 'Direct material cost', 'data': []}
        indirect_material_cost = {'sr': '2', 'name': 'Indirect material cost', 'data': []}
        direct_labour_cost = {'sr': '3', 'name': 'Direct labour cost', 'data': []}
        thirdparty_contractor_cost = {'sr': '4', 'name': 'Thirdparty cost (Contractor)', 'data': []}
        thirdparty_subcontractor_cost = {'sr': '5', 'name': 'Thirdparty cost (Subcontractor)', 'data': []}

        get_direct_material = self.env['projectdir.material.cost'].search([('project_line_id', 'in',
                                                                            self.project_order_line.ids)])
        get_indirect_material = self.env['projectindir.material.cost'].search([('project_line_id', 'in',
                                                                                self.project_order_line.ids)])
        get_direct_labour_cost = self.env['projectdir.labour.cost'].search([('project_line_id', 'in',
                                                                             self.project_order_line.ids)])
        get_thirdparty_contractor_cost = self.env['project.thirdparty.cost.contractor'].search(
            [('project_line_id', 'in', self.project_order_line.ids)])
        get_thirdparty_subcontractor_cost = self.env['project.thirdparty.cost.subcontractor'].search(
            [('project_line_id', 'in', self.project_order_line.ids)])

        to_group_array = {
            'direct_material_cost': get_direct_material,
            'indirect_material_cost': get_indirect_material,
            'direct_labour_cost': get_direct_labour_cost,
            'thirdparty_contractor_cost': get_thirdparty_contractor_cost,
            'thirdparty_subcontractor_cost': get_thirdparty_subcontractor_cost
        }

        for key, value in to_group_array.items():
            item_no = 1
            group_by_product = {}
            for k, g in groupby(value, lambda x: x.product_id):
                if k in group_by_product:
                    group_by_product[k].extend(list(g))
                else:
                    group_by_product[k] = list(g)
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
                    total_qty += grouped_product.qty
                    uom = grouped_product.product_uom_label or ''
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

    def compute_project_cost_estimate(self):
        summary_line = []

        for line in self.project_cost_estimate_line:
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


class ProjectBudgetApplicablePlan(models.Model):
    _name = 'project.budget.line'
    _description = 'Project Budget Line'

    name = fields.Char()
    description = fields.Many2one('product.product', string="Description")
    amount = fields.Integer(string="Amount")
    currency = fields.Many2one('res.currency', string="Currency")
    applicable_date = fields.Date(string="Applicable date", default=fields.Date.today())
    complete_date = fields.Date(string="Complete date", default=fields.Date.today())
    remark = fields.Text(string="Remark")
    project_budget_id = fields.Many2one('project.project', string="PBAP ID")
    budget_approval_id = fields.Many2one('budget.approval', ondelete='cascade')


class ProjectCostExpenseLine(models.Model):
    _name = 'project.expense.order.line'
    _description = 'Project Expense Line'

    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')
    product_uom_label = fields.Char()
    particular_ids = fields.Many2one('expense.order.line.particular')
    product_id = fields.Many2one('product.product', string='Product', domain=[('is_material', '=', True)],
                                 change_default=True, ondelete='restrict')
    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Volume Weight', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))

    project_cost_estimate_id = fields.Many2one('project.project', string='Project Reference', required=True,
                                               ondelete='cascade', index=True, copy=False)
    budget_approval_id = fields.Many2one('budget.approval', ondelete='cascade')
    name = fields.Text(string='Description')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    remark = fields.Char(string="Remark", default="N/A")
    product_uom_qty = fields.Float(compute="_compute_product_qty", string='Ordered Quantity',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"), ('line_expense_section', "Expense Section")], default=False,
        help="Technical field for UX purpose.")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    currency_id = fields.Many2one('res.currency')

    @api.depends('Pcs', 'length', 'width', 'height')
    def _compute_product_qty(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            pcs = 1 if line.Pcs < 1 else line.Pcs
            length = 1 if line.length < 1 else line.length
            width = 1 if line.width < 1 else line.width
            height = 1 if line.height < 1 else line.height

            product_uom_qty = pcs * length * width * height

            line.update({
                'product_uom_qty': product_uom_qty,
            })

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
        view_id = self.env.ref('ideatime_project.view_expense_line_cbm_calc').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.expense.order.line',
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


class ProjectOrderLine(models.Model):
    _name = 'project.order.line'
    _description = 'Project Order Line'

    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

    order_id = fields.Many2one('project.project')
    budget_approval_id = fields.Many2one('budget.approval', ondelete='cascade')

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    invoice_lines = fields.Many2many('account.move.line', 'project_order_line_invoice_rel', 'order_line_id',
                                     'invoice_line_id', string='Invoice Lines', copy=False)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', store=True, readonly=True, default='no')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
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
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id',
                                                         string='User entered custom product attribute values')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create variants')
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

    salesman_id = fields.Many2one(related='order_id.user_id', store=True, string='Salesperson', readonly=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)
    order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', readonly=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    analytic_line_ids = fields.One2many('account.analytic.line', 'so_line', string="Analytic lines")
    is_expense = fields.Boolean('Is expense',
                                help="Is true if the sales order line comes from an expense or a vendor bills")
    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
                                         " They are not copied when duplicating a sales order.")

    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    item_order_confirm_ids = fields.One2many('project.item.order.confirm.line', 'project_line_id')
    client_demand_ids = fields.One2many('project.order.client.demand.line', 'project_line_id')

    order_line_direct_material_cost_ids = fields.One2many('projectdir.material.cost', 'project_line_id')

    size = fields.Char('Size/Service Specification')
    particular_ids = fields.Many2one('material.particular')

    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Volume Weight', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))
    remark = fields.Char(string="Remark", default="N/A")

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

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
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

    def get_sale_order_line_multiline_description_sale(self, product):
        return product.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_variants(self):
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        product_attribute_with_is_custom = self.product_custom_attribute_value_ids.mapped(
            'attribute_value_id.attribute_id')

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

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)
        self.product_uom_qty = self.volume_weight

    def calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_project.view_project_budget_line_cbm_calc').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.order.line',
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
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def open_order_agreement(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_project.view_project_order_agreement_line').id

        return {
            'name': _('Additional Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def open_material_cost(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_project.view_project_material_cost_line').id

        return {
            'name': _('Material Cost Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def _action_launch_stock_rule(self):

        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.product_id.type in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
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
            values.update({
                'project_id': group_id.project_id.id,
            })
            product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
                                                  line.order_id.partner_shipping_id.property_stock_customer, line.name,
                                                  line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True


class ProjectItemOrderConfirmation(models.Model):
    _name = 'project.item.order.confirm.line'
    _description = 'Project Item Order Confirmation'

    particular_id = fields.Char(string='Particular')
    description = fields.Text('Description')
    project_line_id = fields.Many2one('project.order.line')


class ProjectClientDemand(models.Model):
    _name = 'project.order.client.demand.line'
    _description = 'Project Client Demand'

    particular_id = fields.Char(string='Particular')
    description = fields.Text('Description')
    project_line_id = fields.Many2one('project.order.line')


class ProjectDirectMaterialCost(models.Model):
    _inherit = 'projectdir.material.cost'

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

                # name=fields.Char()        

    product_id = fields.Many2one('product.product', required=True, string='Item', domain="[('is_material', '=', True)]")
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    project_line_id = fields.Many2one('project.order.line')
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)

    order_id = fields.Many2one(related='project_line_id.order_id', store=True, string='Order Reference', readonly=True)
    product_updatable = fields.Boolean(string='Can Edit Product', readonly=True, default=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id',
                                                         string='User entered custom product attribute values')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create variants')
    is_expense = fields.Boolean('Is expense',
                                help="Is true if the sales order line comes from an expense or a vendor bills")

    customer_lead = fields.Float(
        'Delivery Lead Time', required=True, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    route_id = fields.Many2one('stock.location.route', string='Route', ondelete='restrict')
    qty_delivered_method = fields.Selection([
        ('manual', 'Manual'),
        ('analytic', 'Analytic From Expenses'),
        ('stock_move', 'Stock Moves')
    ], string="Method to update delivered qty",
        compute_sudo=True, store=True, readonly=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")

    qty_delivered = fields.Float('Delivered Quantity', copy=False,
                                 compute_sudo=True, store=True, digits='Product Unit of Measure',
                                 default=0.0)
    qty_delivered_manual = fields.Float('Delivered Manually', copy=False,
                                        digits='Product Unit of Measure', default=0.0)

    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_label = fields.Char()

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
        for move in self.project_direct_move_ids.filtered(lambda r: r.state != 'cancel'):
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
            if line.product_id:
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
                lambda r: float_compare(r.product_uom_qty, values['product_uom_qty'],
                                        precision_digits=precision) != 0)._update_line_quantity(values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        result = super(ProjectDirectMaterialCost, self).write(values)
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
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, uom=self.product_uom.id)

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
            # date=self.order_id.date_order,
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
                # date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)

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

        # values = super(OrderLineLotBOQ, self)._prepare_procurement_values(group_id)
        values = {}
        self.ensure_one()
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'projectdir_line_id': self.id,
            # 'date_planned': date_planned,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
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
                    'project_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                    # 'project_id': line.order_id.project_id.id,
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
            quant_uom = line.product_id.uom_id
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

    @api.onchange('length', 'width', 'height', 'Pcs')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.pcs > 0:
            self.qty = (self.length * self.width * self.height * self.pcs)


class ProjectInDirectMaterialCost(models.Model):
    _inherit = 'projectindir.material.cost'

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

    product_id = fields.Many2one('product.product', required=True, string='Item', domain="[('is_material', '=', True)]")
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    project_line_id = fields.Many2one('project.order.line')
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True)
    project_line_id = fields.Many2one('project.order.line')
    order_id = fields.Many2one(related='project_line_id.order_id', store=True, string='Order Reference', readonly=True)
    product_updatable = fields.Boolean(string='Can Edit Product', readonly=True, default=True)
    product_uom_qty = fields.Float(string='Ordered Quantity', compute='_compute_amount',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'sale_order_line_id',
                                                         string='User entered custom product attribute values')
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value',
                                                              string='Product attribute values that do not create variants')
    is_expense = fields.Boolean('Is expense',
                                help="Is true if the sales order line comes from an expense or a vendor bills")

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
    ], string="Method to update delivered qty", compute_sudo=True, store=True, readonly=True,
        help="According to product configuration, the delivered quantity can be automatically computed by mechanism :\n"
             "  - Manual: the quantity is set manually on the line\n"
             "  - Analytic From expenses: the quantity is the quantity sum from posted expenses\n"
             "  - Timesheet: the quantity is the sum of hours recorded on tasks linked to this sale line\n"
             "  - Stock Moves: the quantity comes from confirmed pickings\n")

    qty_delivered = fields.Float('Delivered Quantity', copy=False, compute_sudo=True, store=True,
                                 digits='Product Unit of Measure', default=0.0)
    qty_delivered_manual = fields.Float('Delivered Manually', copy=False,
                                        digits='Product Unit of Measure', default=0.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_label = fields.Char()

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
        for move in self.project_indirect_move_ids.filtered(lambda r: r.state != 'cancel'):
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
            if line.product_id:
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
                lambda r: float_compare(r.product_uom_qty, values['product_uom_qty'],
                                        precision_digits=precision) != 0)._update_line_quantity(values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        result = super(ProjectInDirectMaterialCost, self).write(values)
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
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, uom=self.product_uom.id)

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
            # date=self.order_id.date_order,
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
                # date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)

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

        # values = super(OrderLineLotBOQ, self)._prepare_procurement_values(group_id)
        values = {}
        self.ensure_one()
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'projectindir_line_id': self.id,
            # 'date_planned': date_planned,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
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
                    'project_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                    # 'project_id': line.order_id.project_id.id,
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
            quant_uom = line.product_id.uom_id
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


class ProjectDirectLabourCost(models.Model):
    _name = 'projectdir.labour.cost'
    _description = 'Project Direct Labour Cost'

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
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    # on_hand = fields.Float(string='On Hand', compute='_compute_sale')
    project_line_id = fields.Many2one('project.order.line')


class ProjectThridPartyCostContractor(models.Model):
    _name = 'project.thirdparty.cost.contractor'
    _description = 'Project Third Party Cost Contractor'

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
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    project_line_id = fields.Many2one('project.order.line')


class ProjectThridPartyCostSubContractor(models.Model):
    _name = 'project.thirdparty.cost.subcontractor'
    _description = 'Project Third Party Cost SubContractor'

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
    pcs = fields.Float(string='Pcs', default=1.0, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1.0, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1.0, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1.0, copy=False, digits=(12, 3))
    qty = fields.Float(string='Qty', compute='_compute_amount')
    product_uom = fields.Many2one('uom.uom', string='Unit')
    unit_price = fields.Float(string="Unit Price")
    product_uom_label = fields.Char()
    project_line_id = fields.Many2one('project.order.line')
