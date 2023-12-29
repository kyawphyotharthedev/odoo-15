from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json
import io
from odoo.tools import date_utils
import base64

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

FETCH_RANGE = 2500

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


class InsPartnerAgeing(models.TransientModel):
    _inherit = "ins.partner.ageing"

    project_ids = fields.Many2many('project.project', string='Project')
    proj_type_ids = fields.Many2many('project.type', string='Project Type')

    def write(self, vals):
        if not vals.get('project_ids'):
            vals.update({'project_ids': [(5,)]})
        if not vals.get('proj_type_ids'):
            vals.update({'proj_type_ids': [(5,)]})

        ret = super(InsPartnerAgeing, self).write(vals)
        return ret

    def get_filters(self, default_filters={}):

        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('customer_rank', '>', 0),
                                  ('supplier_rank', '>', 0),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]

        partners = self.partner_ids if self.partner_ids else self.env['res.partner'].search(partner_company_domain)
        categories = self.partner_category_ids if self.partner_category_ids else self.env[
            'res.partner.category'].search([])
        project_types = self.proj_type_ids if self.proj_type_ids else self.env['project.type'].search([])
        projects = self.project_ids if self.project_ids else self.env['project.project'].search([])

        filter_dict = {
            'partner_ids': self.partner_ids.ids,
            'partner_category_ids': self.partner_category_ids.ids,
            'proj_type_ids': self.proj_type_ids.ids,
            'project_ids': self.project_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'as_on_date': self.as_on_date,
            'type': self.type,
            'partner_type': self.partner_type,
            'bucket_1': self.bucket_1,
            'bucket_2': self.bucket_2,
            'bucket_3': self.bucket_3,
            'bucket_4': self.bucket_4,
            'bucket_5': self.bucket_5,
            'include_details': self.include_details,
            'project_types_list': [(pj.id, pj.display_name) for pj in project_types],
            'projects_list': [(pj.id, pj.name, pj.proj_type_id.parent_types.ids + [pj.proj_type_id.id]) for pj in projects],
            'partners_list': [(p.id, p.name) for p in partners],
            'category_list': [(c.id, c.name) for c in categories],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict

    def process_filters(self):
        ''' To show on report headers'''

        data = self.get_filters(default_filters={})

        filters = {}

        filters['bucket_1'] = data.get('bucket_1')
        filters['bucket_2'] = data.get('bucket_2')
        filters['bucket_3'] = data.get('bucket_3')
        filters['bucket_4'] = data.get('bucket_4')
        filters['bucket_5'] = data.get('bucket_5')

        if data.get('partner_ids', []):
            filters['partners'] = self.env['res.partner'].browse(data.get('partner_ids', [])).mapped('name')
        else:
            filters['partners'] = ['All']
        if data.get('as_on_date', False):
            filters['as_on_date'] = data.get('as_on_date')

        if data.get('company_id'):
            filters['company_id'] = data.get('company_id')
        else:
            filters['company_id'] = ''

        if data.get('type'):
            filters['type'] = data.get('type')

        if data.get('partner_type'):
            filters['partner_type'] = data.get('partner_type')

        if data.get('partner_category_ids', []):
            filters['categories'] = self.env['res.partner.category'].browse(
                data.get('partner_category_ids', [])).mapped('name')
        else:
            filters['categories'] = ['All']

        if data.get('include_details'):
            filters['include_details'] = True
        else:
            filters['include_details'] = False
        if data.get('project_ids', []):
            filters['projects'] = self.env['project.project'].browse(data.get('project_ids', [])).mapped('name')
        else:
            filters['projects'] = ['All']
        if data.get('proj_type_ids', []):
            filters['project_types'] = self.env['project.type'].browse(data.get('proj_type_ids', [])).mapped('name')
        else:
            filters['project_types'] = ['All']

        filters['project_types_list'] = data.get('project_types_list')
        filters['projects_list'] = data.get('projects_list')
        filters['partners_list'] = data.get('partners_list')
        filters['category_list'] = data.get('category_list')
        filters['company_name'] = data.get('company_name')

        return filters

    def build_where_clause(self, data=False):
        if not data:
            data = self.get_filters(default_filters={})

        if data:

            WHERE = '(1=1)'

            if data.get('proj_type_ids', []):
                project_type_filter_list = data['proj_type_ids']
                project_type_filter_obj = self.env['project.type'].browse(project_type_filter_list)
                for project_type in project_type_filter_obj:
                    project_type_filter_list += project_type.right_ids.ids
                project_type_filter_list = list(set(project_type_filter_list))
                WHERE += ' AND l.proj_type_id IN %s' % str(tuple(project_type_filter_list) + tuple([0]))
            if data.get('project_ids', []):
                WHERE += ' AND l.project_id IN %s' % str(tuple(data.get('project_ids')) + tuple([0]))

        return WHERE

    def process_detailed_data(self, offset=0, partner=0, fetch_range=FETCH_RANGE):
        as_on_date = self.as_on_date
        period_dict = self.prepare_bucket_list()
        period_list = [period_dict[a]['name'] for a in period_dict]
        company_id = self.env.company

        type = ('receivable', 'payable')
        if self.type:
            type = tuple([self.type, 'none'])
        WHERE = self.build_where_clause()
        proj_type_ids = self.proj_type_ids or self.env['project.type'].search([])
        project_type = '( ' + ' ,'.join(str(x) for x in proj_type_ids.ids) + ')'
        project_ids = self.project_ids or self.env['project.project'].search([])
        project = '( ' + ' ,'.join(str(x) for x in project_ids.ids) + ')'

        offset = offset * fetch_range
        count = 0

        if partner:

            sql = """
                    SELECT COUNT(*)
                    FROM
                        account_move_line AS l
                    LEFT JOIN
                        account_move AS m ON m.id = l.move_id
                    LEFT JOIN
                        account_account AS a ON a.id = l.account_id
                    LEFT JOIN
                        account_account_type AS ty ON a.user_type_id = ty.id
                    LEFT JOIN
                        account_journal AS j ON l.journal_id = j.id
                    WHERE
                        l.balance <> 0
                        AND m.state = 'posted'
                        AND ty.type IN %s
                        AND l.proj_type_id IN %s
                        AND l.project_id IN %s
                        AND l.partner_id = %s
                        AND l.date <= '%s'
                        AND l.company_id = %s
                """ % (type, project_type, project, partner, as_on_date, company_id.id)
            self.env.cr.execute(sql)
            count = self.env.cr.fetchone()[0]

            SELECT = """SELECT m.name AS move_name,
                                m.id AS move_id,
                                l.date AS date,
                                l.date_maturity AS date_maturity, 
                                j.name AS journal_name,
                                cc.id AS company_currency_id,
                                a.name AS account_name, """

            for period in period_dict:
                if period_dict[period].get('start') and period_dict[period].get('stop'):
                    SELECT += """ CASE 
                                    WHEN 
                                        COALESCE(l.date_maturity,l.date) >= '%s' AND 
                                        COALESCE(l.date_maturity,l.date) <= '%s'
                                    THEN
                                        sum(l.balance) +
                                        sum(
                                            COALESCE(
                                                (SELECT 
                                                    SUM(amount)
                                                FROM account_partial_reconcile
                                                WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                                )
                                            ) -
                                        sum(
                                            COALESCE(
                                                (SELECT 
                                                    SUM(amount) 
                                                FROM account_partial_reconcile 
                                                WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                                )
                                            )
                                    ELSE
                                        0
                                    END AS %s,""" % (period_dict[period].get('stop'),
                                                     period_dict[period].get('start'),
                                                     as_on_date,
                                                     as_on_date,
                                                     'range_' + str(period),
                                                     )
                elif not period_dict[period].get('start'):
                    SELECT += """ CASE 
                                    WHEN 
                                        COALESCE(l.date_maturity,l.date) >= '%s' 
                                    THEN
                                        sum(
                                            l.balance
                                            ) +
                                        sum(
                                            COALESCE(
                                                (SELECT 
                                                    SUM(amount)
                                                FROM account_partial_reconcile
                                                WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                                )
                                            ) -
                                        sum(
                                            COALESCE(
                                                (SELECT 
                                                    SUM(amount) 
                                                FROM account_partial_reconcile 
                                                WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                                )
                                            )
                                    ELSE
                                        0
                                    END AS %s,""" % (
                        period_dict[period].get('stop'), as_on_date, as_on_date, 'range_' + str(period))
                else:
                    SELECT += """ CASE
                                    WHEN
                                        COALESCE(l.date_maturity,l.date) <= '%s' 
                                    THEN
                                        sum(
                                            l.balance
                                            ) +
                                        sum(
                                            COALESCE(
                                                (SELECT 
                                                    SUM(amount)
                                                FROM account_partial_reconcile
                                                WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                                )
                                            ) -
                                        sum(
                                            COALESCE(
                                                (SELECT 
                                                    SUM(amount) 
                                                FROM account_partial_reconcile 
                                                WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                                )
                                            )
                                    ELSE
                                        0
                                    END AS %s """ % (
                        period_dict[period].get('start'), as_on_date, as_on_date, 'range_' + str(period))

            sql = """
                    FROM
                        account_move_line AS l
                    LEFT JOIN
                        account_move AS m ON m.id = l.move_id
                    LEFT JOIN
                        account_account AS a ON a.id = l.account_id
                    LEFT JOIN
                        account_account_type AS ty ON a.user_type_id = ty.id
                    LEFT JOIN
                        account_journal AS j ON l.journal_id = j.id
                    LEFT JOIN 
                        res_currency AS cc ON l.company_currency_id = cc.id
                    WHERE
                        l.balance <> 0
                        AND m.state = 'posted'
                        AND ty.type IN %s
                        AND l.partner_id = %s
                        AND l.date <= '%s'
                        AND l.company_id = %s
                        AND %s
                        
                    GROUP BY
                        l.date,l.date_maturity, m.id, m.name, j.name, a.name, cc.id
                    OFFSET %s ROWS
                    FETCH FIRST %s ROWS ONLY
                """ % (type, partner, as_on_date, company_id.id, WHERE, offset, fetch_range)
            self.env.cr.execute(SELECT + sql)

            move_lines = []
            for m in self.env.cr.dictfetchall():
                if (m['range_0'] or m['range_1'] or m['range_2'] or m['range_3'] or m['range_4'] or m['range_5']):
                    move_lines.append(m)

            if move_lines:
                return count, offset, move_lines, period_list
            else:
                return 0, 0, [], []

    def process_data(self):

        period_dict = self.prepare_bucket_list()
        data = self.get_filters(default_filters={})

        domain = ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)]
        if self.partner_type == 'customer':
            domain.append(('customer_rank', '>', 0))
        if self.partner_type == 'supplier':
            domain.append(('supplier_rank', '>', 0))

        if self.partner_category_ids:
            domain.append(('category_id', 'in', self.partner_category_ids.ids))

        partner_ids = self.partner_ids or self.env['res.partner'].search(domain)
        as_on_date = self.as_on_date
        company_currency_id = self.env.company.currency_id.id
        company_id = self.env.company

        type = ('receivable', 'payable')
        if self.type:
            type = tuple([self.type, 'none'])

        partner_dict = {}
        for partner in partner_ids:
            partner_dict.update({partner.id: {}})

        partner_dict.update({'Total': {}})
        for period in period_dict:
            partner_dict['Total'].update({period_dict[period]['name']: 0.0})
        partner_dict['Total'].update({'total': 0.0, 'partner_name': 'ZZZZZZZZZ'})
        partner_dict['Total'].update({'company_currency_id': company_currency_id})
        for partner in partner_ids:
            partner_dict[partner.id].update({'partner_name': partner.name})
            total_balance = 0.0

            sql = """
                SELECT
                    COUNT(*) AS count
                FROM
                    account_move_line AS l
                LEFT JOIN
                    account_move AS m ON m.id = l.move_id
                LEFT JOIN
                    account_account AS a ON a.id = l.account_id
                LEFT JOIN
                    account_account_type AS ty ON a.user_type_id = ty.id
                WHERE
                    l.balance <> 0
                    AND m.state = 'posted'
                    AND ty.type IN %s
                    AND l.partner_id = %s
                    AND l.date <= '%s'
                    AND l.company_id = %s
                    """ % (type, partner.id, as_on_date, company_id.id)
            self.env.cr.execute(sql)
            fetch_dict = self.env.cr.dictfetchone() or 0.0
            count = fetch_dict.get('count') or 0.0

            if count:
                for period in period_dict:

                    where = " AND l.date <= '%s' AND l.partner_id = %s AND COALESCE(l.date_maturity,l.date) " % (
                        as_on_date, partner.id)

                    if period_dict[period].get('start') and period_dict[period].get('stop'):
                        where += " BETWEEN '%s' AND '%s'" % (
                            period_dict[period].get('stop'), period_dict[period].get('start'))
                    elif not period_dict[period].get('start'):  # ie just
                        where += " >= '%s'" % (period_dict[period].get('stop'))
                    else:
                        where += " <= '%s'" % (period_dict[period].get('start'))
                    if data.get('proj_type_ids', []):
                        project_type_filter_list = data['proj_type_ids']
                        project_type_filter_obj = self.env['project.type'].browse(project_type_filter_list)
                        for project_type in project_type_filter_obj:
                            project_type_filter_list += project_type.children.ids
                        project_type_filter_list = list(set(project_type_filter_list))
                        where += ' AND l.proj_type_id IN %s' % str(tuple(project_type_filter_list) + tuple([0]))

                    sql = """
                            SELECT
                                sum(
                                l.balance
                                ) AS balance,
                            sum(
                                COALESCE(
                                    (SELECT 
                                        SUM(amount)
                                    FROM account_partial_reconcile
                                    WHERE credit_move_id = l.id AND max_date <= '%s'), 0
                                    )
                                ) AS sum_debit,
                            sum(
                                COALESCE(
                                    (SELECT 
                                        SUM(amount) 
                                    FROM account_partial_reconcile 
                                    WHERE debit_move_id = l.id AND max_date <= '%s'), 0
                                    )
                                ) AS sum_credit
                            FROM
                                account_move_line AS l
                            LEFT JOIN
                                account_move AS m ON m.id = l.move_id
                            LEFT JOIN
                                account_account AS a ON a.id = l.account_id
                            LEFT JOIN
                                account_account_type AS ty ON a.user_type_id = ty.id
                            WHERE
                            l.balance <> 0
                            AND m.state = 'posted'
                            AND ty.type IN %s
                            AND l.company_id = %s
                        """ % (as_on_date, as_on_date, type, company_id.id)
                    amount = 0.0
                    self.env.cr.execute(sql + where)
                    fetch_dict = self.env.cr.dictfetchall() or 0.0

                    if not fetch_dict[0].get('balance'):
                        amount = 0.0
                    else:
                        amount = fetch_dict[0]['balance'] + fetch_dict[0]['sum_debit'] - fetch_dict[0]['sum_credit']
                        total_balance += amount

                    partner_dict[partner.id].update({period_dict[period]['name']: amount})
                    partner_dict['Total'][period_dict[period]['name']] += amount
                partner_dict[partner.id].update({'count': count})
                partner_dict[partner.id].update({'pages': self.get_page_list(count)})
                partner_dict[partner.id].update({'single_page': True if count <= FETCH_RANGE else False})
                partner_dict[partner.id].update({'total': total_balance})
                partner_dict['Total']['total'] += total_balance
                partner_dict[partner.id].update({'company_currency_id': company_currency_id})
                partner_dict['Total'].update({'company_currency_id': company_currency_id})
            else:
                partner_dict.pop(partner.id, None)
        return period_dict, partner_dict
