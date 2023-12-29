# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IdeatimeBudget(models.Model):
    _inherit = 'budget.approval'
    _check_company_auto = True
    company_id = fields.Many2one('res.company', string="Company", related="project_id.company_id", store=True,
                                 required=True, default=lambda self: self.env.company)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if not domain:
            domain = []
        domain.append(('company_id', '=', self.env.company.id))
        if self.env.context.get('allowed_user'):
            domain.append(('allowed_user_ids', '=', self.env.context.get('allowed_user')))
        return super(IdeatimeBudget, self).search_read(domain=domain, fields=fields,
                                                        offset=offset, limit=limit, order=order)

    def get_budget_ids(self):
        budget_ids = self.env['ideatime.budget'].search_read(context={'allowed_user': self.env.uid})
        return budget_ids
 