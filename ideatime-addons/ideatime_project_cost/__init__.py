# -*- coding: utf-8 -*-

from . import models
from . import wizard

from odoo import api, SUPERUSER_ID, _


def _configure_journals(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    company_ids = env['res.company'].search([('chart_template_id', '!=', False)])
    for company_id in company_ids:
        journal_id = env['account.journal'].search([
            ('name', '=', _('Cost Journal')),
            ('company_id', '=', company_id.id),
            ('type', '=', 'general')], limit=1)
        if not journal_id:
            env['account.journal'].create({
                'name': _('Cost Journal'),
                'type': 'general',
                'code': 'CSJ',
                'company_id': company_id.id,
                'show_on_dashboard': False
            })
