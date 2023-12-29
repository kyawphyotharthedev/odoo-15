from odoo import fields, models


class ShopType(models.Model):
    _name = "shop.type"
    _description = "Shop Type"

    name = fields.Char('Name', required=True)
