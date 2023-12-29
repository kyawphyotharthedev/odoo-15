from odoo import api, fields, models, _


class StockLocation(models.Model):
    _inherit = "stock.location"

    location_expense_account_id = fields.Many2one('account.account', string='Expense Account',
                                                  default=lambda self: self.env.ref(
                                                      'l10n_generic_coa.1_cost_of_goods_sold',
                                                      raise_if_not_found=False))


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_project_in_done_stage(self):
        for picking in self:
            picking.project_in_done_stage = False
            if picking.project_id.proj_type_stage_id.stage_state == 'done':
                picking.project_in_done_stage = True

    project_cost_account_move_ids = fields.One2many('account.move', 'project_cost_picking_id', string='Project Cost Account Moves')
    return_picking_id = fields.Many2one('stock.picking', string='Return Picking')
    project_in_done_stage = fields.Boolean(compute='_compute_project_in_done_stage', string='In Done Stage')


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _prepare_picking_default_values(self):
        vals = super(ReturnPicking, self)._prepare_picking_default_values()
        vals['return_picking_id'] = self.picking_id.id
        return vals
