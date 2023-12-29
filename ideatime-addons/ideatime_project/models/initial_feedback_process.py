from odoo import api, fields, models, _


class InitialFeedbackProcess(models.Model):
    _name = 'initial.feedback.process'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Initial Feedback Process'

    def _get_revised(self):
        for record in self:
            record.update({
                'revise_count': len(record.child_ids)
            })

    project_id = fields.Many2one('project.project')
    parent_id = fields.Many2one('initial.feedback.process')
    child_ids = fields.One2many('initial.feedback.process', 'parent_id')
    revise_count = fields.Integer(string='Revise Count', compute='_get_revised', readonly=True)

    name = fields.Char(required=True, index=True, string="Name")
    partner_id = fields.Many2one('res.partner', required=True)
    employee_id = fields.Many2one("hr.employee")

    first_meeting = fields.Selection([
        ('ideatime_office', 'Ideatime Office'),
        ('client_office', 'Client Office'),
        ('shop', 'Shop'), ('site', 'Site'), ('phone', 'Phone'), ('other', 'Other')], default='ideatime_office')

    to_know_company = fields.Selection([
        ('facebook', 'Facebook'),
        ('website', 'Website'),
        ('reffered', 'Reffered'), ('offline_media', 'Offline Media'), ('enquiry', 'Enquiry'),
        ('social_net', 'Social  Network'), ('community', 'Community'), ('marketing', 'Marketing')], default='marketing')

    customer_interest = fields.Selection([
        ('sector', 'Service Sector'),
        ('service_line', 'Service Line'),
        ('particular', 'Particular'),
        ('function', 'Function')])

    project_type_id = fields.Many2one('project.type')
    reactive_contact_info_ids = fields.One2many('project.reactive.contact.info', 'survey_id')

    industry_type_id = fields.Many2one('industry.type', string="Industry Type")
    business_group_id = fields.Many2one('business.group', string="Business Group")
    business_type_id = fields.Many2one('business.type', string="Business Type")
    service_gp_id = fields.Many2one('service.category.group', string="Service Group")
    service_sector_id = fields.Many2one('service.category.sector', string="Service Sector")
    sale_item_cate_id = fields.Many2one('sale.item.category', string="Category")
    demand = fields.Text('Demand')
    project_site = fields.Char('Project Site')
    city = fields.Char('City')
    township = fields.Char('Township')
    street = fields.Char('Street')
    ward = fields.Char('Ward')
    land_number = fields.Char('No.')
    site_name = fields.Char('Site name / Building name')
    tower_type = fields.Char('Tower Type')
    tower_no = fields.Char('Tower No')
    floor = fields.Char('Floor')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit to Process'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('revised', 'Revised')
    ], string='Status', readonly=True, copy=False, index=True,
        tracking=True, default='draft')
    rev_number = fields.Integer('Rev Number', copy=False, default=1)

    @api.onchange('city', 'township', 'street', 'ward', 'land_number', 'site_name', 'tower_type', 'tower_no', 'floor')
    def _compute_material_code_name(self):

        project_site = [[lambda: '', lambda: '(' + self.site_name + ')'][self.site_name != False](),
                        self.tower_type or '', self.tower_no or '', self.floor or '',
                        [lambda: '', lambda: 'No.:' + self.land_number][self.land_number != False](), self.street or '',
                        self.ward or '', self.township or '', self.city or '']
        self.project_site = " ".join(str(site) for site in filter(lambda r: r != '', project_site))

    @api.model
    def create(self, vals):
        res = super(InitialFeedbackProcess, self).create(vals)
        if not res.name:
            res.update({'name': self.env['ir.sequence'].next_by_code('IniFeedProc') or _('New')})
        return res

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_submit(self):
        return self.write({'state': 'submit'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def make_revise(self):
        for cur_rec in self:
            vals = {
                'name': 'Rev:' + str(cur_rec.rev_number) + ' ' + str(cur_rec.name),
                'state': 'revised',
                'parent_id': cur_rec.id
            }
            cur_rec.copy(default=vals)
            cur_rec.state = 'draft'
            cur_rec.rev_number += 1
