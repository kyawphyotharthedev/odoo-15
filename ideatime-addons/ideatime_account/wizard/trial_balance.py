from odoo import fields, models

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


class InsTrialBalance(models.TransientModel):
    _inherit = "ins.trial.balance"

    project_ids = fields.Many2many('project.project', string='Project')
    proj_type_ids = fields.Many2many('project.type', string='Project Type')

    def write(self, vals):
        if not vals.get('proj_type_ids'):
            vals.update({'proj_type_ids': [(5,)]})
        if not vals.get('project_ids'):
            vals.update({'project_ids': [(5,)]})

        ret = super(InsTrialBalance, self).write(vals)
        return ret

    def process_filters(self, data):
        ''' To show on report headers'''
        res = super(InsTrialBalance, self).process_filters(data)

        # data = self.get_filters(default_filters={})

        if data.get('proj_type_ids', []):
            res['project_types'] = self.env['project.type'].browse(data.get('proj_type_ids', [])).mapped('name')
        else:
            res['project_types'] = ['All']
        if data.get('project_ids', []):
            res['projects'] = self.env['project.project'].browse(data.get('projects_ids', [])).mapped('name')
        else:
            res['projects'] = ['All']

        res['project_types_list'] = data.get('project_types_list')
        res['projects_list'] = data.get('projects_list')

        return res

    def process_data(self, data):
        if data:
            cr = self.env.cr
            WHERE = '(1=1)'

            if data.get('journal_ids', []):
                WHERE += ' AND j.id IN %s' % str(tuple(data.get('journal_ids')) + tuple([0]))

            if data.get('account_ids', []):
                WHERE += ' AND a.id IN %s' % str(tuple(data.get('account_ids')) + tuple([0]))

            if data.get('analytic_ids', []):
                WHERE += ' AND anl.id IN %s' % str(tuple(data.get('analytic_ids')) + tuple([0]))
            if data.get('proj_type_ids', []):
                project_type_filter_list = data['proj_type_ids']
                project_type_filter_obj = self.env['project.type'].browse(project_type_filter_list)
                for project_type in project_type_filter_obj:
                    project_type_filter_list += project_type.children.ids
                project_type_filter_list = list(set(project_type_filter_list))
                WHERE += ' AND l.proj_type_id IN %s' % str(tuple(project_type_filter_list) + tuple([0]))
            if data.get('project_ids', []):
                WHERE += ' AND l.project_id IN %s' % str(tuple(data.get('project_ids')) + tuple([0]))
            if data.get('company_id', False):
                WHERE += ' AND l.company_id = %s' % data.get('company_id')

            if data.get('target_moves') == 'posted_only':
                WHERE += " AND m.state = 'posted'"

            if data.get('account_ids'):
                account_ids = self.env['account.account'].browse(data.get('account_ids'))
            else:
                account_ids = self.env['account.account'].search([('company_id', '=', data.get('company_id'))])
            company_currency_id = self.env.company.currency_id

            move_lines = {x.code: {'name': x.name, 'code': x.code, 'id': x.id,
                                   'initial_debit': 0.0, 'initial_credit': 0.0, 'initial_balance': 0.0,
                                   'debit': 0.0, 'credit': 0.0, 'balance': 0.0,
                                   'ending_credit': 0.0, 'ending_debit': 0.0, 'ending_balance': 0.0,
                                   'company_currency_id': company_currency_id.id} for x in
                          account_ids}  # base for accounts to display
            retained = {}
            retained_earnings = 0.0
            retained_credit = 0.0
            retained_debit = 0.0
            total_deb = 0.0
            total_cre = 0.0
            total_bln = 0.0
            total_init_deb = 0.0
            total_init_cre = 0.0
            total_init_bal = 0.0
            total_end_deb = 0.0
            total_end_cre = 0.0
            total_end_bal = 0.0
            for account in account_ids:
                currency = account.company_id.currency_id or self.env.company.currency_id

                WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get(
                    'date_from') + " AND l.date <= '%s'" % data.get('date_to')
                WHERE_CURRENT += " AND a.id = %s" % account.id
                sql = ('''
                    SELECT
                        COALESCE(SUM(l.debit),0) AS debit,
                        COALESCE(SUM(l.credit),0) AS credit,
                        COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_CURRENT
                cr.execute(sql)

                op = cr.dictfetchone()
                deb = op['debit']
                cre = op['credit']
                bln = op['balance']
                move_lines[account.code]['debit'] = deb
                move_lines[account.code]['credit'] = cre
                move_lines[account.code]['balance'] = bln

                end_blns = bln
                end_cr = cre
                end_dr = deb

                total_deb += deb
                total_cre += cre
                total_bln += bln
            if self.strict_range:
                retained = {'RETAINED': {'name': 'Unallocated Earnings', 'code': '', 'id': 'RET',

                                         'credit': 0.0, 'debit': 0.0, 'balance': 0.0,

                                         'company_currency_id': company_currency_id.id}}
            subtotal = {'SUBTOTAL': {
                'name': 'Total',
                'code': '',
                'id': 'SUB',

                'credit': company_currency_id.round(total_cre),
                'debit': company_currency_id.round(total_deb),
                'balance': company_currency_id.round(total_bln),

                'company_currency_id': company_currency_id.id}}

            if self.show_hierarchy:
                move_lines = self.prepare_hierarchy(move_lines)
            return [move_lines, retained, subtotal]

    def get_filters(self, default_filters={}):

        self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(company_domain)
        analytics = self.analytic_ids if self.analytic_ids else self.env['account.analytic.account'].search(
            company_domain)
        project_types = self.proj_type_ids if self.proj_type_ids else self.env['project.type'].search([])
        projects =self.project_ids if self.project_ids else self.env['project.project'].search([])

        filter_dict = {
            'proj_type_ids': self.proj_type_ids.ids,
            'project_ids': self.project_ids.ids,
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids,
            'analytic_ids': self.analytic_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'display_accounts': self.display_accounts,
            'show_hierarchy': self.show_hierarchy,
            'strict_range': self.strict_range,
            'target_moves': self.target_moves,
            'project_types_list': [(pj.id, pj.display_name) for pj in project_types],
            'projects_list': [(pj.id, pj.name, pj.proj_type_id.parent_types.ids + [pj.proj_type_id.id]) for pj in projects],
            'journals_list': [(j.id, j.name) for j in journals],
            'accounts_list': [(a.id, a.name) for a in accounts],
            'analytics_list': [(anl.id, anl.name) for anl in analytics],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict
