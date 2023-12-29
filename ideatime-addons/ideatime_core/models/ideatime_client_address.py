from odoo import models, fields


class IdeaTimeClientAddress(models.Model):
    _name = 'ideatime.address'
    _description = 'IdeaTime Client Address'

    address_id = fields.Many2one('res.partner', 'ideatime_address_id')
    street = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    country_id = fields.Many2one('res.country')
    mobile = fields.Char()
    email = fields.Char()
    website = fields.Char()
