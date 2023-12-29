import json
import datetime
import math
import re

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
SIZE_BACK_ORDER_NUMERING = 3


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    project_id = fields.Many2one('project.project', string='Project', required=True)
    project_site_id = fields.Char(related="project_id.project_site")
    project_name = fields.Char(compute="_compute_project_name")
    project_client_id = fields.Char(related="project_id.partner_id.name")
    analytic_account_id = fields.Many2one('account.analytic.account')

    @api.onchange('project_id')
    def onchange_project_id(self):

        analytic_account_obj = self.env['account.analytic.account'].search([('name', '=', self.project_id.name)])
        self.analytic_account_id = False
        for analytic in analytic_account_obj:
            self.analytic_account_id = analytic.id

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