from odoo import fields, models
from odoo.exceptions import UserError


class ProjectCostJournalGenerate(models.TransientModel):
    _name = "project.cost.journal.generate"

    def _default_project(self):
        return self.env['project.project'].browse(self._context.get('active_id'))

    def picking_domain(self):
        return [
            ('project_id', '=', self._context.get('active_id')),
            ('project_cost_account_move_ids', '=', False),
            ('state', '=', 'done'),
            '|', ('picking_type_id.code', '=', 'outgoing'),
            '&', ('picking_type_id.code', '=', 'incoming'), ('return_picking_id', '!=', False)
        ]

    def _default_picking(self):
        return self.env['stock.picking'].search(self.picking_domain())

    project_id = fields.Many2one('project.project', string='Project', readonly=True, default=_default_project)
    picking_ids = fields.Many2many('stock.picking', string='Pickings', domain=picking_domain, default=_default_picking)
    date = fields.Date(string='Date', default=fields.Date.context_today)

    def get_cost_journal(self):
        cost_journal = self.env['account.journal'].search(
            [('company_id', '=', self.env.company.id), ('code', '=', 'CSJ'), ('type', '=', 'general')], limit=1)
        if not cost_journal:
            raise UserError('No Cost Journal found for this company.')
        return cost_journal

    def _prepare_account_move_return_vals(self, picking, cost_journal, account_move_line_credit):
        return {
            'project_cost_picking_id': picking.id,
            'ref': 'Project Cost for Picking %s' % account_move_line_credit.name,
            'journal_id': cost_journal.id,
            'date': self.date,
            'project_id': self.project_id.id,
            'line_ids': [(0, 0, {
                'name': 'Project Cost Credit Line for Picking %s' % account_move_line_credit.name,
                'account_id': picking.location_id.location_expense_account_id.id,
                'partner_id': picking.partner_id.id,
                'debit': 0,
                'credit': account_move_line_credit.credit,
            }), (0, 0, {
                'name': 'Project Cost Debit Line for Picking %s' % account_move_line_credit.name,
                'account_id': account_move_line_credit.account_id.id,
                'partner_id': picking.partner_id.id,
                'debit': account_move_line_credit.credit,
                'credit': 0,
            })]
        }

    def _prepare_account_move_outgoing_vals(self, picking, cost_journal, account_move_line_debit):
        return {
            'project_cost_picking_id': picking.id,
            'ref': 'Project Cost for Picking %s' % account_move_line_debit.name,
            'journal_id': cost_journal.id,
            'date': self.date,
            'project_id': self.project_id.id,
            'line_ids': [(0, 0, {
                'name': 'Project Cost Credit Line for Picking %s' % account_move_line_debit.name,
                'account_id': account_move_line_debit.account_id.id,
                'partner_id': picking.partner_id.id,
                'debit': 0,
                'credit': account_move_line_debit.debit,
            }), (0, 0, {
                'name': 'Project Cost Debit Line for Picking %s' % account_move_line_debit.name,
                'account_id': picking.location_id.location_expense_account_id.id,
                'partner_id': picking.partner_id.id,
                'debit': account_move_line_debit.debit,
                'credit': 0,
            })]
        }

    def generate_journals(self):
        cost_journal = self.get_cost_journal()
        for picking in self.picking_ids:
            for stock_move in picking.move_ids_without_package:
                for account_move in stock_move.account_move_ids:
                    if picking.return_picking_id and picking.picking_type_id.code == 'incoming':
                        account_move_line_credit = account_move.line_ids.filtered(lambda l: l.credit > 0)

                        if not account_move_line_credit or len(account_move_line_credit) > 1:
                            raise UserError('Something wrong with Account Move Line Debit, %s - %s.' % (
                                picking.name, stock_move.product_id.name))

                        account_move_vals = self._prepare_account_move_return_vals(picking, cost_journal,
                                                                                   account_move_line_credit)
                    else:
                        account_move_line_debit = account_move.line_ids.filtered(lambda l: l.debit > 0)

                        if not account_move_line_debit or len(account_move_line_debit) > 1:
                            raise UserError('Something wrong with Account Move Line Debit, %s - %s.' % (
                                picking.name, stock_move.product_id.name))

                        account_move_vals = self._prepare_account_move_outgoing_vals(picking, cost_journal,
                                                                                     account_move_line_debit)
                    cost_account_move = self.env['account.move'].create(account_move_vals)
                    cost_account_move.action_post()
