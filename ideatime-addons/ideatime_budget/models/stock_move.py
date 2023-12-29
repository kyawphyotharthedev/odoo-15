
from odoo import fields, models,api


class StockMove(models.Model):
    _inherit = "stock.move"

    budgetdir_line_id = fields.Many2one('budget.parta.cost', 'Direct Material Cost Line', index=True)
    # created_budgetdir_line_id = fields.Many2one(
    #     'budget.parta.cost', 'Created Direct Material Cost Line',
    #     ondelete='set null', index='btree_not_null', readonly=True, copy=False)
    # @api.model
    # def _prepare_merge_moves_distinct_fields(self):
    #     distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
    #     distinct_fields += ['created_budgetdir_line_id']
    #     return distinct_fields

    def _get_new_picking_values(self):
        origins = self.filtered(lambda m: m.origin).mapped('origin')
        origins = list(dict.fromkeys(origins)) # create a list of unique items
        # Will display source document if any, when multiple different origins
        # are found display a maximum of 5
        if len(origins) == 0:
            origin = False
        else:
            origin = ','.join(origins[:5])
            if len(origins) > 5:
                origin += "..."
        partners = self.mapped('partner_id')
        partner = len(partners) == 1 and partners.id or False
        group_id = self.mapped('group_id')
        return {
            'origin': origin,
            'company_id': self.mapped('company_id').id,
            'move_type': self.mapped('group_id').move_type or 'direct',
            'partner_id': partner,
            'picking_type_id': self.mapped('picking_type_id').id,
            'location_id': self.mapped('location_id').id,
            'location_dest_id': self.mapped('location_dest_id').id,
            'project_id': group_id.project_id.id,
            'budget_id': group_id.budget_id.id,
        }


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['project_id', 'projectdir_line_id', 'projectindir_line_id', 'budget_id', 'budgetdir_line_id',
                   'partner_id']
        fields += ['budgetindir_line_id', 'partner_id']
        return fields


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    budget_id = fields.Many2one('budget.approval', string="Budget")
