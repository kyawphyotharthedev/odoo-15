# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    report_template_id = fields.Many2one('ir.ui.view', string="Report Template",
                                         domain="[('key', 'ilike', 'partner_base_report')]")
