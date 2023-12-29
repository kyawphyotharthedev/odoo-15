# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    project_id = fields.Many2one('project.project', string='Project', compute="_compute_project", required=True)

    @api.depends('line_ids')
    def _compute_project(self):
        for record in self:
            project = False
            for line in record.line_ids:
                if not project:
                    project = line.project_id
                elif project != line.project_id:
                    project = False
            record.project_id = project

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        payment_vals['project_id'] = self.project_id.id
        return payment_vals
