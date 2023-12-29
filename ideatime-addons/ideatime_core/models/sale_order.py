# -*- coding: utf-8 -*-

from odoo import fields, api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    project_id = fields.Many2one('project.project', string='Project', required=True)
    project_client_id = fields.Char(related="project_id.partner_id.name")

    project_site_id = fields.Char(related="project_id.project_site")
    finance_senior_manager = fields.Many2one('res.users', compute="_compute_finance_manager", store=True)
    project_senior_manger = fields.Many2one('res.users', compute="_compute_project_approve", store=True)
    project_director = fields.Many2one('res.users', compute="_compute_project_director", store=True)
    project_director_approve = fields.Boolean(default="False", compute="_compute_project_director_approve")
    project_name = fields.Char(compute="_compute_project_name")
    is_contract_client = fields.Boolean(string='Is Contract Client', default=False)
    w_state = fields.Selection([
        ('initial', 'Initial'),
        ('order_agreement', 'Order Agreegment Confirm'),
        ('budget', 'Budget Available'),
        ('check', 'Detail Check'),
        ('approve', 'Project Implement Approve'),
    ], string='Workflow Status', readonly=True, copy=False, index=True, tracking=True,
        default='initial')

    @api.onchange('project_id')
    def _compute_is_contract_client(self):
        for record in self:
            if record.project_id.is_contract_client:
                record.is_contract_client = True

    @api.depends('finance_senior_manager')
    def _compute_finance_approve(self):
        for record in self:
            if record.finance_senior_manager == record.current_user:
                record.finance_approve = True
            else:
                record.finance_approve = False

    @api.depends('project_id.finance_senior_management_id')
    def _compute_finance_manager(self):
        for record in self:
            if record.project_id.finance_senior_management_id:
                record.finance_senior_manager = record.project_id.finance_senior_management_id
            else:
                record.finance_senior_manager = None

    @api.depends('project_senior_manger')
    def _compute_project_senior_approve(self):
        for record in self:
            if record.project_senior_manger == record.current_user:
                record.project_senior_approve = True
            else:
                record.project_senior_approve = False

    @api.depends('project_director')
    def _compute_project_director_approve(self):
        for record in self:
            if record.project_director == record.current_user:
                record.project_director_approve = True
            else:
                record.project_director_approve = False

    @api.depends('project_id.director')
    def _compute_project_director(self):
        for record in self:
            if record.project_id.director:
                record.project_director = record.project_id.director

    @api.depends('project_id.project_senior_management_id')
    def _compute_project_approve(self):
        for record in self:
            if record.project_id.project_senior_management_id:
                record.project_senior_manger = record.project_id.project_senior_management_id

    @api.onchange('project_id')
    def set_customer_name(self):
        for rec in self:
            if rec.project_id:
                rec.partner_id = rec.project_id.partner_id

    @api.onchange('project_id')
    def _compute_project_name(self):
        for record in self:
            service_project_name = []
            if record.project_client_id:
                service_project_name.append(record.project_client_id)

            if record.project_id.cate_sector_id:
                service_project_name.append(str(record.project_id.cate_sector_id.name))
            if record.project_id.cate_line_id:
                service_project_name.append(str(record.project_id.cate_line_id.name))

            if record.project_id.manual_project_name:
                service_project_name.append(str(record.project_id.manual_project_name))

            record.project_name = " ".join(str(x) for x in service_project_name)
