from odoo import models, fields, api


class ShopList(models.Model):
    _inherit = 'shop.list'

    def _default_company(self):
        return self.env['res.company']._company_default_get('shop.list')

    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    country_id = fields.Many2one('res.country')
    region = fields.Many2one('customer.region', string='Region')

    city = fields.Many2one('customer.city', string='City')

    township = fields.Many2one('customer.township', string='Township')
    address = fields.Text()

    name = fields.Char(index=True)
    # display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    date = fields.Date(index=True)
    title = fields.Many2one('res.partner.title')
    parent_id = fields.Many2one('shop.list', string='Related Company', index=True)
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    child_ids = fields.One2many('shop.list', 'parent_id', string='Contacts', domain=[
        ('active', '=', True)])  # force "active_test" domain to bypass _search() override
    ref = fields.Char(string='Internal Reference', index=True)

    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)
    user_id = fields.Many2one('res.users', string='Salesperson',
                              help='The internal user in charge of this contact.')
    vat = fields.Char(string='Tax ID',
                      help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    bank_ids = fields.One2many('res.partner.bank', 'partner_id', string='Banks')
    website = fields.Char()
    comment = fields.Text(string='Notes')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Other address'),
         ("private", "Private Address"),
         ], string='Address Type',
        default='contact',
        help="Used by Sales and Purchase Apps to select the relevant address depending on the context.")
    email = fields.Char()
    is_company = fields.Boolean(string='Is a Company', default=False,
                                help="Check if the contact is a company, otherwise it is a person")
    industry_id = fields.Many2one('res.partner.industry', 'Industry')
    # company_type is only an interface field, do not use it in business logic
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    compute='_compute_company_type', inverse='_write_company_type')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)
    color = fields.Integer(string='Color Index', default=0)
    user_ids = fields.One2many('res.users', 'partner_id', string='Users', auto_join=True)

    contact_address = fields.Char(string='Complete Address')
    company_name = fields.Char('Company Name')
    function = fields.Char(string='Job Position ')
    employee = fields.Boolean(help="Check this box if this contact is an Employee.")
    mobile = fields.Char()
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang,
                            help="All the emails and documents sent to this contact will be translated in this language.")

    @api.onchange('country_id', 'region', 'city', 'township', 'street')
    def _compute_address(self):
        # for record in self:

        add = []
        add = [self.street or '', self.township.name or '', self.city.name or '', self.region.name or '',
               self.country_id.name or '']
        self.address = ", ".join(str(x) for x in add)

    @api.onchange('country_id')
    def set_region_to(self):
        for rec in self:
            if rec.country_id:
                ids = self.env['customer.region'].search([('country_id', '=', rec.country_id.id)])
                return {
                    'domain': {'region': [('id', 'in', ids.ids)], }
                }

    @api.onchange('region')
    def set_city_to(self):
        for rec in self:
            rec.country_id = rec.region.country_id
            if rec.region:
                ids = self.env['customer.city'].search([('region', '=', rec.region.id)])
                return {
                    'domain': {'city': [('id', 'in', ids.ids)], }
                }

    @api.onchange('city')
    def set_township_to(self):
        for rec in self:
            rec.region = rec.city.region
            if rec.city:
                ids = self.env['customer.township'].search([('city', '=', rec.city.id)])
                return {
                    'domain': {'township': [('id', 'in', ids.ids)], }
                }

    @api.onchange('township')
    def _set_city_region(self):
        for rec in self:
            rec.city = rec.township.city

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
