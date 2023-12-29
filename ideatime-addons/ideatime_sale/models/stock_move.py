# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    direct_line_id = fields.Many2one('direct.material.cost', 'Direct Material Cost Line')
    in_direct_line_id = fields.Many2one('in.direct.material.cost', 'In Direct Material Cost Line')
