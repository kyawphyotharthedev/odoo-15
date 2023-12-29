# -*- coding: utf-8 -*-
from odoo import fields, models, api


class IdeaTimeUOM(models.Model):
    _inherit = "uom.category"
    _check_company_auto = True
    company_id = fields.Many2one('res.company', string="Company", store=True,
                                 required=True, default=lambda self: self.env.company)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if not domain:
            domain = []
        domain.append(('company_id', '=', self.env.company.id))
        return super(IdeaTimeUOM, self).search_read(domain=domain, fields=fields,
                                                    offset=offset, limit=limit, order=order)


