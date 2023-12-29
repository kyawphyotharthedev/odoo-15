from odoo import models, fields


class User(models.Model):
    _inherit = 'res.users'

    service_sector_ids = fields.Many2many('service.category.sector', 'user_service_sector', 'sector_id', 'user_id',
                                          string='Sectors')
