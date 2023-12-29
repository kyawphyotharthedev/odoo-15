from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = 'res.partner'

    ideatime_address_id = fields.One2many('ideatime.address', 'address_id')

    project_site = fields.Char(string='Project Site')

    ideatime_region = fields.Many2one('customer.region', string='Region')
    ideatime_city = fields.Many2one('customer.city', string='City ')
    shop = fields.Many2one('shop.list', string='Shop name')
    ideatime_township = fields.Many2one('customer.township', string='Township')

    street = fields.Char(string='Street')
    ward = fields.Char(string='Ward')
    land_number = fields.Char(string='No.')
    site_name = fields.Char(string='Site name / Building name')
    tower_type = fields.Char(string='Tower Type')
    tower_no = fields.Char(string='Tower No')
    floor = fields.Char(string='Floor')
    industry_type_id = fields.Many2one('industry.type', string="Industry Type")
    business_group_id = fields.Many2one('business.group', string="Business Type")
    business_type_id = fields.Many2one('business.type', string="Business Category")
    service_channel_id = fields.Many2one('service.channel', string="Service Channel")

    out_of_mail = fields.Char(string='Out of Email')
    custom_id = fields.Char(string="Custom ID")
    comment = fields.Text(string='Notes')
    marketing = fields.Many2one('marketing')

    def _get_name(self):

        res = super(Partner, self)._get_name()
        if self._context.get('show_project_site') and self.project_site:
            res = "%s\n%s" % (res, self.project_site)
        if self._context.get('show_job_position') and self.function:
            res = "%s\n%s" % (res, self.function)
        if self._context.get('show_phone') and self.phone:
            res = "%s\n%s" % (res, self.phone)
        if self._context.get('show_mobile') and self.mobile:
            res = "%s\n%s" % (res, self.mobile)
        if self._context.get('show_mail') and self.email:
            res = "%s\n%s" % (res, self.email)
        if self._context.get('show_note') and self.comment:
            res = "%s\n%s" % (res, self.comment)

        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('parent_id'):

                if vals.get('customer') is True:
                    customer = self.env['res.partner'].search(
                        [('name', '=', vals.get('name')), ('customer', '=', True), ('id', '!=', vals.get('id'))])
                    if customer:
                        raise UserError(_('Exists ! Already a customer exists in this name'))

            if vals.get('supplier') is True:
                supplier = self.env['res.partner'].search(
                    [('name', '=', vals.get('name')), ('supplier', '=', True), ('id', '!=', vals.get('id'))])
                if supplier:
                    raise UserError(_('Exists ! Already a vendor exists in this name'))

        return super(Partner, self).create(vals_list)

    @api.onchange('industry_type_id')
    def set_business_group_to(self):
        self.business_group_id = False
        self.business_type_id = False
        if self.industry_type_id:
            ids = self.env['business.group'].search([('left_id', '=', self.industry_type_id.id)])
            return {
                'domain': {'business_group_id': [('id', 'in', ids.ids)], }
            }

    @api.onchange('business_group_id')
    def set_business_type_to(self):
        self.business_type_id = False
        if self.business_group_id:
            ids = self.env['business.type'].search([('left_id', '=', self.business_group_id.id)])
            return {
                'domain': {'business_type_id': [('id', 'in', ids.ids)], }
            }

    @api.onchange('country_id')
    def set_region_to(self):
        for rec in self:
            if rec.country_id:
                ids = self.env['customer.region'].search([('country_id', '=', rec.country_id.id)])
                return {
                    'domain': {'ideatime_region': [('id', 'in', ids.ids)], }
                }

    @api.onchange('ideatime_region')
    def set_city_to(self):
        for rec in self:
            rec.country_id = rec.ideatime_region.country_id
            if rec.ideatime_region:
                ids = self.env['customer.city'].search([('region', '=', rec.ideatime_region.id)])
                return {
                    'domain': {'ideatime_city': [('id', 'in', ids.ids)], }
                }

    @api.onchange('ideatime_city')
    def set_township_to(self):
        for rec in self:
            rec.ideatime_region = rec.ideatime_city.region
            if rec.ideatime_city:
                ids = self.env['customer.township'].search([('city', '=', rec.ideatime_city.id)])
                return {
                    'domain': {'ideatime_township': [('id', 'in', ids.ids)], }
                }

    @api.onchange('ideatime_township')
    def _set_city_region(self):
        for rec in self:
            rec.ideatime_city = rec.ideatime_township.city

    @api.onchange('country_id', 'ideatime_region', 'ideatime_city', 'ideatime_township', 'street', 'ward', 'land_number',
                  'site_name', 'tower_type', 'tower_no', 'floor')
    def _compute_material_code_name(self):
        project_site = [[lambda: '', lambda: '(' + self.site_name + ')'][self.site_name != False](),
                        self.tower_type or '', self.tower_no or '', self.floor or '',
                        [lambda: '', lambda: ',No.:' + self.land_number][self.land_number != False](), self.street
                        or '',
                        self.ward or '', self.ideatime_township.name or '', ',', self.ideatime_city.name or '', ',',
                        self.ideatime_region.name or '', ',', self.country_id.name or '']
        self.project_site = " ".join(str(site) for site in filter(lambda r: r != '', project_site))
