# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ShopList(models.Model):
    _name = 'shop.list'
    _inherit = ['avatar.mixin']
    _description = 'Shop List'

    name = fields.Char('Shop Name')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    date = fields.Date(default=fields.Date.today(), readonly=True)
    industry_type_id = fields.Many2one('industry.type', string="Industry Type")
    business_group_id = fields.Many2one('business.group', string="Business Type")
    business_type_id = fields.Many2one('business.type', string="Business Category")
    shop_type_id = fields.Many2one('shop.type', string='Shop Type')

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    phone = fields.Char()
    remark = fields.Text(string='Remark')
    vat = fields.Char(string='Tax ID',
                      help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    color = fields.Integer(string='Color Index', default=0)

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = None

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id
