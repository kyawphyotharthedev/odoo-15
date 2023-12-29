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

FETCH_RANGE = 2000


class InsPartnerLedger(models.TransientModel):
    _inherit = "ins.partner.ledger"

    project_ids = fields.Many2many('project.project', string='Project')
    proj_type_ids = fields.Many2many('project.type', string='Project Type')

    def write(self, vals):
        if not vals.get('proj_type_ids'):
            vals.update({'proj_type_ids': [(5,)]})
        if not vals.get('project_ids'):
            vals.update({'project_ids': [(5,)]})

        ret = super(InsPartnerLedger, self).write(vals)
        return ret

    def process_filters(self):
        ''' To show on report headers'''
        res = super(InsPartnerLedger, self).process_filters()

        data = self.get_filters(default_filters={})

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

    def build_where_clause(self, data=False):

        if not data:
            data = self.get_filters(default_filters={})

        if data:

            WHERE = '(1=1)'

            type = ('receivable', 'payable')
            if self.type:
                type = tuple([self.type, 'none'])

            WHERE += ' AND ty.type IN %s' % str(type)

            if data.get('reconciled') == 'reconciled':
                WHERE += ' AND l.amount_residual = 0'
            if data.get('reconciled') == 'unreconciled':
                WHERE += ' AND l.amount_residual != 0'

            if data.get('journal_ids', []):
                WHERE += ' AND j.id IN %s' % str(tuple(data.get('journal_ids')) + tuple([0]))

            if data.get('account_ids', []):
                WHERE += ' AND a.id IN %s' % str(tuple(data.get('account_ids')) + tuple([0]))

            if data.get('proj_type_ids', []):
                project_type_filter_list = data['proj_type_ids']
                project_type_filter_obj = self.env['project.type'].browse(project_type_filter_list)
                for project_type in project_type_filter_obj:
                    project_type_filter_list += project_type.children.ids
                project_type_filter_list = list(set(project_type_filter_list))
                WHERE += ' AND l.proj_type_id IN %s' % str(tuple(project_type_filter_list) + tuple([0]))

            if data.get('project_ids', []):
                WHERE += ' AND l.project_id IN %s' % str(tuple(data.get('project_ids')) + tuple([0]))

            if data.get('partner_ids', []):
                WHERE += ' AND p.id IN %s' % str(tuple(data.get('partner_ids')) + tuple([0]))

            if data.get('company_id', False):
                WHERE += ' AND l.company_id = %s' % data.get('company_id')

            if data.get('target_moves') == 'posted_only':
                WHERE += " AND m.state = 'posted'"
            return WHERE

    def get_filters(self, default_filters={}):
        res = super(InsPartnerLedger, self).get_filters(default_filters={})

        project_types = self.proj_type_ids if self.proj_type_ids else self.env['project.type'].search([])
        projects =self.project_ids if self.project_ids else self.env['project.project'].search([])

        default_filters.update({
            'proj_type_ids': self.proj_type_ids.ids,
            'project_ids': self.project_ids.ids,
            'journal_ids': res['journal_ids'],
            'account_ids': res['account_ids'],
            'partner_ids': res['partner_ids'],
            'partner_category_ids': res['partner_category_ids'],
            'company_id': res['company_id'] and res['company_id'] or False,
            'target_moves': res['target_moves'],
            'initial_balance': res['initial_balance'],
            'date_from': res['date_from'],
            'date_to': res['date_to'],
            'reconciled': res['reconciled'],
            'display_accounts': res['display_accounts'],
            'include_details': res['include_details'],
            'balance_less_than_zero': res['balance_less_than_zero'],
            'balance_greater_than_zero': res['balance_greater_than_zero'],
            'project_types_list': [(pj.id, pj.display_name) for pj in project_types],
            'projects_list': [(pj.id, pj.name, pj.proj_type_id.parent_types.ids + [pj.proj_type_id.id]) for pj in projects],
            'journals_list': [(j[0], j[1]) for j in res['journals_list']],
            'accounts_list': [(a[0], a[1]) for a in res['accounts_list']],
            'partners_list': [(p[0], p[1]) for p in res['partners_list']],
            'category_list': [(c[0], c[1]) for c in res['category_list']],
            'company_name': self.company_id and self.company_id.name,
        })

        return default_filters
