from odoo import fields, api, models


class LocationChecker(models.Model):
    _inherit = 'stock.location'
    reorder_location = fields.Boolean('Is a Reorder Location?')
