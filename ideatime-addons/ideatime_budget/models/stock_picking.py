from odoo import models, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    budget_id = fields.Many2one('budget.approval')
