from odoo import fields, models

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

FETCH_RANGE = 2000


class InsGeneralLedger(models.TransientModel):
    _inherit = "ins.general.ledger"

    project_ids = fields.Many2many('project.project', string='Project')
    proj_type_ids = fields.Many2many('project.type', string='Project Type')

    def write(self, vals):
        if not vals.get('project_ids'):
            vals.update({'project_ids': [(5,)]})
        if not vals.get('proj_type_ids'):
            vals.update({'proj_type_ids': [(5,)]})

        ret = super(InsGeneralLedger, self).write(vals)
        return ret

    def process_filters(self):
        """ To show on report headers"""

        res = super(InsGeneralLedger, self).process_filters()

        data = self.get_filters(default_filters={})

        if data.get('proj_type_ids', []):
            res['project_types'] = self.env['project.type'].browse(data.get('proj_type_ids', [])).mapped('name')
        else:
            res['project_types'] = ['All']
        if data.get('project_ids', []):
            res['projects'] = self.env['project.project'].browse(data.get('projects_ids', [])).mapped('name')
        else:
            res['projects'] = ['All']

        res['projects_list'] = data.get('projects_list')
        res['project_types_list'] = data.get('project_types_list')

        return res

    def build_where_clause(self, data=False):
        if not data:
            data = self.get_filters(default_filters={})

        if data:

            WHERE = '(1=1)'

            if data.get('journal_ids', []):
                WHERE += ' AND j.id IN %s' % str(tuple(data.get('journal_ids')) + tuple([0]))

            if data.get('analytic_ids', []):
                WHERE += ' AND anl.id IN %s' % str(tuple(data.get('analytic_ids')) + tuple([0]))

            if data.get('analytic_tag_ids', []):
                WHERE += ' AND analtag.account_analytic_tag_id IN %s' % str(
                    tuple(data.get('analytic_tag_ids')) + tuple([0]))
            if data.get('proj_type_ids', []):
                project_type_filter_list = data['proj_type_ids']
                project_type_filter_obj = self.env['project.type'].browse(project_type_filter_list)
                for project_type in project_type_filter_obj:
                    project_type_filter_list += project_type.children.ids
                project_type_filter_list = list(set(project_type_filter_list))
                WHERE += ' AND l.proj_type_id IN %s' % str(tuple(project_type_filter_list) + tuple([0]))
            if data.get('partner_ids', []):
                WHERE += ' AND p.id IN %s' % str(tuple(data.get('partner_ids')) + tuple([0]))

            if data.get('company_id', False):
                WHERE += ' AND l.company_id = %s' % data.get('company_id')

            if data.get('target_moves') == 'posted_only':
                WHERE += " AND m.state = 'posted'"

            return WHERE

    def get_filters(self, default_filters={}):

        self.onchange_date_range()
        company_domain = [('company_id', '=', self.env.context.get('company_id'))]
        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('customer_rank', '>', 0),
                                  ('supplier_rank', '>', 0),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]

        journals = self.journal_ids if self.journal_ids else self.env['account.journal'].search(company_domain)
        accounts = self.account_ids if self.account_ids else self.env['account.account'].search(company_domain)
        account_tags = self.account_tag_ids if self.account_tag_ids else self.env['account.account.tag'].search([])
        analytics = self.analytic_ids if self.analytic_ids else self.env['account.analytic.account'].search(
            company_domain)
        analytic_tags = self.analytic_tag_ids if self.analytic_tag_ids else self.env[
            'account.analytic.tag'].sudo().search(
            ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])
        partners = self.partner_ids if self.partner_ids else self.env['res.partner'].search(partner_company_domain)
        projects = self.project_ids if self.project_ids else self.env['project.project'].search([])
        project_types = self.proj_type_ids if self.proj_type_ids else self.env['project.type'].search([])

        filter_dict = {
            'proj_type_ids': self.proj_type_ids.ids,
            'project_ids': self.project_ids.ids,
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids,
            'account_tag_ids': self.account_tag_ids.ids,
            'analytic_ids': self.analytic_ids.ids,
            'analytic_tag_ids': self.analytic_tag_ids.ids,
            'partner_ids': self.partner_ids.ids,
            'company_id': self.company_id and self.company_id.id or False,
            'target_moves': self.target_moves,
            'sort_accounts_by': self.sort_accounts_by,
            'initial_balance': self.initial_balance,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'display_accounts': self.display_accounts,
            'include_details': self.include_details,
            'project_types_list': [(pj.id, pj.display_name) for pj in project_types],
            'projects_list': [(pj.id, pj.name, pj.proj_type_id.parent_types.ids + [pj.proj_type_id.id]) for pj in projects],
            'journals_list': [(j.id, j.name) for j in journals],
            'accounts_list': [(a.id, a.name) for a in accounts],
            'account_tag_list': [(a.id, a.name) for a in account_tags],
            'partners_list': [(p.id, p.name) for p in partners],
            'analytics_list': [(anl.id, anl.name) for anl in analytics],
            'analytic_tag_list': [(anltag.id, anltag.name) for anltag in analytic_tags],
            'company_name': self.company_id and self.company_id.name,
        }
        filter_dict.update(default_filters)
        return filter_dict
