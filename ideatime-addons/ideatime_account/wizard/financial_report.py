# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import re

from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json
import io
from odoo.tools import date_utils
import base64

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

DATE_DICT = {
    '%m/%d/%Y': 'mm/dd/yyyy',
    '%Y/%m/%d': 'yyyy/mm/dd',
    '%m/%d/%y': 'mm/dd/yy',
    '%d/%m/%Y': 'dd/mm/yyyy',
    '%d/%m/%y': 'dd/mm/yy',
    '%d-%m-%Y': 'dd-mm-yyyy',
    '%d-%m-%y': 'dd-mm-yy',
    '%m-%d-%Y': 'mm-dd-yyyy',
    '%m-%d-%y': 'mm-dd-yy',
    '%Y-%m-%d': 'yyyy-mm-dd',
    '%f/%e/%Y': 'm/d/yyyy',
    '%f/%e/%y': 'm/d/yy',
    '%e/%f/%Y': 'd/m/yyyy',
    '%e/%f/%y': 'd/m/yy',
    '%f-%e-%Y': 'm-d-yyyy',
    '%f-%e-%y': 'm-d-yy',
    '%e-%f-%Y': 'd-m-yyyy',
    '%e-%f-%y': 'd-m-yy'
}


class InsFinancialReport(models.TransientModel):
    _inherit = "ins.financial.report"
    _description = "Financial Reports"

    project_ids = fields.Many2many('project.project', string='Project')
    proj_type_ids = fields.Many2many('project.type', string='Project Type')

    def write(self, vals):
        if not vals.get('project_ids'):
            vals.update({'project_ids': [(5,)]})
        if not vals.get('proj_type_ids'):
            vals.update({'proj_type_ids': [(5,)]})

        ret = super(InsFinancialReport, self).write(vals)
        return ret

    def get_report_values(self):
        self.ensure_one()

        self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]
        project_ids = self.env['project.project'].search([])
        journal_ids = self.env['account.journal'].search(company_domain)
        project_type_ids = self.env['project.type'].search([])
        analytics = self.env['account.analytic.account'].search(company_domain)
        analytic_tags = self.env['account.analytic.tag'].sudo().search(
            ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])

        data = dict()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['date_from', 'enable_filter', 'debit_credit', 'date_to', 'date_range',
             'account_report_id', 'target_move', 'view_format', 'journal_ids',
             'analytic_ids', 'analytic_tag_ids', 'strict_range',
             'company_id', 'enable_filter', 'date_from_cmp', 'date_to_cmp', 'label_filter', 'filter_cmp',
             'proj_type_ids', 'project_ids'])[0]
        data['form'].update({'journals_list': [(j.id, j.name) for j in journal_ids]})
        data['form'].update({'project_types_list': [(pj.id, pj.display_name) for pj in project_type_ids]})
        data['form'].update({'project_list': [(pj.id, pj.name, pj.proj_type_id.parent_types.ids + [pj.proj_type_id.id]) for pj in project_ids]})
        data['form'].update({'analytics_list': [(j.id, j.name) for j in analytics]})
        data['form'].update({'analytic_tag_list': [(j.id, j.name) for j in analytic_tags]})

        if self.enable_filter:
            data['form']['debit_credit'] = False

        date_from, date_to = False, False
        used_context = {}
        used_context['date_from'] = self.date_from or False
        used_context['date_to'] = self.date_to or False

        used_context['strict_range'] = True
        used_context['company_id'] = self.env.company.id
        used_context['journal_ids'] = self.journal_ids.ids
        used_context['project_ids'] = self.project_ids.ids
        used_context['proj_type_ids'] = self.proj_type_ids.ids
        used_context['analytic_account_ids'] = self.analytic_ids
        used_context['analytic_tag_ids'] = self.analytic_tag_ids
        used_context['state'] = data['form'].get('target_move', '')
        data['form']['used_context'] = used_context

        comparison_context = {}
        comparison_context['strict_range'] = True
        comparison_context['company_id'] = self.env.company.id

        comparison_context['journal_ids'] = self.journal_ids.ids
        comparison_context['project_ids'] = self.project_ids.ids
        comparison_context['proj_type_ids'] = self.proj_type_ids.ids
        comparison_context['analytic_account_ids'] = self.analytic_ids
        comparison_context['analytic_tag_ids'] = self.analytic_tag_ids
        if self.filter_cmp == 'filter_date':
            comparison_context['date_to'] = self.date_to_cmp or ''
            comparison_context['date_from'] = self.date_from_cmp or ''
        else:
            comparison_context['date_to'] = False
            comparison_context['date_from'] = False
        comparison_context['state'] = self.target_move or ''
        data['form']['comparison_context'] = comparison_context

        report_lines, initial_balance, current_balance, ending_balance = self.get_account_lines(data.get('form'))
        data['currency'] = self.env.company.currency_id.id
        data['report_lines'] = report_lines
        data['initial_balance'] = initial_balance or 0.0
        data['current_balance'] = current_balance or 0.0
        data['ending_balance'] = ending_balance or 0.0
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            data['form']['rtype'] = 'CASH'
        elif self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0'):
            data['form']['rtype'] = 'PANDL'
        else:
            if self.strict_range:
                data['form']['rtype'] = 'OTHER'
            else:
                data['form']['rtype'] = 'PANDL'
        return data

    def _compute_account_balance(self, accounts, report):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            if self.account_report_id != \
                    self.env.ref(
                        'account_dynamic_reports.ins_account_financial_report_cash_flow0') and self.strict_range:

                context = dict(self._context, strict_range=True)

                # Validation
                if report.type in ['accounts', 'account_type'] and not report.range_selection:
                    raise UserError(_('Please choose "Custom Date Range" for the report head %s') % (report.name))

                if report.type in ['accounts', 'account_type'] and report.range_selection == 'from_the_beginning':
                    context.update({'strict_range': False})
                # For equity
                if report.type in ['accounts', 'account_type'] and report.range_selection == 'current_date_range':
                    if self.date_to and self.date_from:
                        context.update({'strict_range': True, 'initial_bal': False})
                    else:
                        raise UserError(_('From date and To date are mandatory to generate this report'))
                if report.type in ['accounts', 'account_type'] and report.range_selection == 'initial_date_range':
                    if self.date_from:
                        context.update(
                            {'strict_range': True, 'initial_bal': True, 'date_from': self.date_from, 'date_to': False})
                    else:
                        raise UserError(_('From date is mandatory to generate this report'))
                tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
            else:
                tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if self._context.get('project_ids', []):
                wheres.append(' account_move_line.project_id IN %s' % str(tuple(self._context.get('project_ids')) + tuple([0])))
            if self._context.get('proj_type_ids', []):
                project_type_filter_list = self._context['proj_type_ids']
                project_type_filter_obj = self.env['project.type'].browse(project_type_filter_list)
                for project_type in project_type_filter_obj:
                    project_type_filter_list += project_type.children.ids
                project_type_filter_list = list(set(project_type_filter_list))
                wheres.append(
                    ' account_move_line.proj_type_id IN %s' % str(tuple(project_type_filter_list) + tuple([0])))
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                      " FROM " + tables + \
                      " WHERE account_id IN %s " \
                      + filters + \
                      " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def get_account_lines(self, data):
        lines = []
        initial_balance = 0.0
        current_balance = 0.0
        ending_balance = 0.0
        account_report = self.account_report_id
        child_reports = account_report._get_children_by_order(strict_range=self.strict_range)
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            if not data.get('used_context').get('date_from', False):
                raise UserError(_('Start date is mandatory!'))
            cashflow_context = data.get('used_context')
            initial_to = fields.Date.from_string(data.get('used_context').get('date_from')) - timedelta(days=1)
            cashflow_context.update({'date_from': False, 'date_to': fields.Date.to_string(initial_to)})
            initial_balance = self.with_context(cashflow_context)._compute_report_balance(child_reports). \
                get(self.account_report_id.id)['balance']
            current_balance = res.get(self.account_report_id.id)['balance']
            ending_balance = initial_balance + current_balance
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            company_id = self.env.company
            currency_id = company_id.currency_id
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * int(report.sign),
                'parent': report.parent_id.id if report.parent_id.type in ['accounts', 'account_type'] else 0,
                'self_id': report.id,
                'type': 'report',
                'style_type': 'main',
                'precision': currency_id.decimal_places,
                'symbol': currency_id.symbol,
                'position': currency_id.position,
                'list_len': [a for a in range(0, report.level)],
                'level': report.level,
                'company_currency_id': self.env.company.currency_id.id,
                'account_type': report.type or False,  # used to underline the financial report balances
                'fin_report_type': report.type,
                'display_detail': report.display_detail
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * int(report.sign)

            lines.append(vals)
            if report.display_detail == 'no_detail':
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'account': account.id,
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * int(report.sign) or 0.0,
                        'type': 'account',
                        'parent': report.id if report.type in ['accounts', 'account_type'] else 0,
                        'self_id': 50,
                        'style_type': 'sub',
                        'precision': currency_id.decimal_places,
                        'symbol': currency_id.symbol,
                        'position': currency_id.position,
                        'list_len': [a for a in range(0, report.level)],
                        'level': report.level + 1,
                        'company_currency_id': self.env.company.currency_id.id,
                        'account_type': account.internal_type,
                        'fin_report_type': report.type,
                        'display_detail': report.display_detail
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not currency_id.is_zero(vals['debit']) or not currency_id.is_zero(vals['credit']):
                            flag = True
                    if not currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * int(report.sign)
                        if not currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        return lines, initial_balance, current_balance, ending_balance
