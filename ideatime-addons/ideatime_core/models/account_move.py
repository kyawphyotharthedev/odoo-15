# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order')
    project_id = fields.Many2one('project.project', string='Project', required=True)
    project_site_id = fields.Char(related="project_id.project_site")
    project_name = fields.Char(compute="_compute_project_name")
    project_client_id = fields.Char(related="project_id.partner_id.name")

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

    @api.onchange('project_id', 'line_ids', 'invoice_line_ids')
    def _project_onchange(self):
        for record in self:
            if record.project_id:
                record.line_ids.update({
                    'project_id': record.project_id.id,
                    'proj_type_id': record.project_id.proj_type_id.id,
                })


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    project_id = fields.Many2one('project.project', string='Project',  compute="_compute_project_data",
                                 store=True)
    proj_type_id = fields.Many2one('project.type', string='Project Type', compute="_compute_project_data", store=True)

    @api.depends('move_id.project_id')
    @api.onchange('account_id')
    def _compute_project_data(self):
        for record in self:
            if record.move_id.project_id:
                record.update({
                    'project_id': record.move_id.project_id.id,
                    'proj_type_id': record.move_id.project_id.proj_type_id.id,
                })

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for record in res:
            if record.move_id.project_id:
                record._compute_project_data()
        return res
