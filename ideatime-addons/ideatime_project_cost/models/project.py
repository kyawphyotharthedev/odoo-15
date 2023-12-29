from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    def _compute_project_cost_account_moves(self):
        for project in self:
            project.project_cost_account_move_ids = self.env['account.move'].search([
                ('project_id', '=', project.id),
                ('project_cost_picking_id', 'in', project.picking_ids.ids)
            ])
            project.cost_account_move_count = len(project.project_cost_account_move_ids)

    project_cost_account_move_ids = fields.Many2many('account.move', compute=_compute_project_cost_account_moves)
    cost_account_move_count = fields.Integer(compute=_compute_project_cost_account_moves,
                                             string='# of Cost Account Moves')
