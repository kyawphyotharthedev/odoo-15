from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    project_cost_picking_id = fields.Many2one('stock.picking', string='Project Cost Picking')
