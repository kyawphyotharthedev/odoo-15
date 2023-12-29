from odoo import models, fields


class CostType(models.Model):
    _name = 'cost.type'
    _description = 'Cost Type'

    name = fields.Char(string='Name', required=True)
    # option_ids = fields.One2many('cost.option', 'type_id')


# class CostOption(models.Model):
#     _name = 'cost.option'
#     _description = 'Cost Option'
#
#     name = fields.Char(string='Name', required=True)
#     type_id = fields.Many2one('cost.type', string='Cost Type', required=True)
#     require_detail = fields.Boolean(string='Detail Required')
