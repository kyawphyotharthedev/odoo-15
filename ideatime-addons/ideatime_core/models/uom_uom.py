from odoo import fields, models


class UoM(models.Model):
    _inherit = 'uom.uom'

    uom_label = fields.Char(string="Label")
