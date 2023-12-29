from odoo import fields, api, models, _


class Marketing(models.Model):
    _name = 'marketing'
    _description = 'Marketing'

    name = fields.Char()


class NewItemLine(models.Model):
    _name = 'new.item.line'
    _description = 'New Item Line'

    particular = fields.Char(string="Particular")
    product_id = fields.Many2one('product.product', string="Item Code", domain=[('is_sale_item', '=', True)])
    name = fields.Text(string="Description")
    unit = fields.Many2one('uom.uom')
    photo = fields.Binary()
    size = fields.Char()
    remark = fields.Text()
    followup_progress_id = fields.Many2one('follow.up.progress')


class SaleItemLine(models.Model):
    _name = 'sale.item.line'
    _description = 'Sale Item Line'

    particular = fields.Char(string="Particular")
    barcode = fields.Char()
    product_id = fields.Many2one('product.product', string="Item Code")
    name = fields.Text(string="Description", readonly=True)
    unit = fields.Many2one('uom.uom')
    size = fields.Char()
    remark = fields.Text()
    photo = fields.Binary()
    followup_progress_id = fields.Many2one('follow.up.progress')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.barcode = self.product_id.barcode
        self.photo = self.product_id.image_small
        self.unit = self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}


class MeetingMinutesLine(models.Model):
    _name = 'meetingmins.record.line'
    _description = 'Meeting Minutes Line'

    name = fields.Char(string="Particular")
    discuss_content = fields.Char(string="Discussion Content")
    meeting_result = fields.Char()
    meeting_mins_record_id = fields.Many2one('meeting.minutes.record')


class ParticularLine(models.Model):
    _name = 'particular.line'
    _description = 'Particular Line'

    name = fields.Text()
    meeting_mins_record_id = fields.Many2one('meeting.minutes.record')
    design_proposal_id = fields.Many2one('design.proposal')


class MeetingType(models.Model):
    _name = 'meeting.type'
    _description = 'Meeting Type'

    name = fields.Char()


class FirstDemandItem(models.Model):
    _name = 'first.demand.item'
    _description = 'First Demand Item'

    meet_visit_process_id = fields.Many2one('meet.visit.process')
    date = fields.Date()
    agreement_file_upload = fields.Binary(string="Agreement File Upload")


class AdditionalItem(models.Model):
    _name = 'additional.item'
    _description = 'Additional Item'

    meet_visit_process_id = fields.Many2one('meet.visit.process')
    date = fields.Date()
    agreement_file_upload = fields.Binary(string="Agreement File Upload")


class FollowupProgress(models.Model):
    _name = 'follow.up.progress'
    _description = 'Follow Up Progress'

    meet_visit_process_id = fields.Many2one('meet.visit.process')
    start_date = fields.Date(default=fields.Date.today(), readonly=True)
    end_date = fields.Date(readonly=True)
    task = fields.Char("Task")
    remark = fields.Text()
    appendix_id = fields.One2many('appendix', 'followup_progress_id')
    saleitem_line_id = fields.One2many('sale.item.line', 'followup_progress_id')
    newitem_line_id = fields.One2many('new.item.line', 'followup_progress_id')

    def action_end_date_confirm(self):
        self.write({

            'end_date': fields.Datetime.now()
        })


class MeetingMinutesRecord(models.Model):
    _name = 'meeting.minutes.record'
    _description = 'Meeting Minutes Record'

    user_ids = fields.Many2many('res.users')
    meet_visit_process_id = fields.Many2one('meet.visit.process')
    discussion = fields.Char("Discussion Title", compute="_compute_discussion")

    client_participate = fields.Char(compute="_compute_client_participate")
    client_pic_ids = fields.One2many('client.pic', 'meeting_mins_record_id')
    date = fields.Date()
    meeting_type_id = fields.Many2one('meeting.type')
    meeting_location = fields.Text()
    particular_id = fields.One2many('particular.line', 'meeting_mins_record_id')
    meetingmins_line_id = fields.One2many('meetingmins.record.line', 'meeting_mins_record_id')
    partner_id = fields.Many2one('res.partner', related="meet_visit_process_id.partner_id")

    @api.onchange('client_pic_ids')
    def _compute_client_participate(self):

        for record in self:
            total_pic = []
            for line in record.client_pic_ids:
                total_pic.append(line.pic_id.name)
                client_pic = ", ".join(str(x) for x in total_pic)
                record.client_participate = client_pic

    @api.onchange('particular_id')
    def _compute_discussion(self):

        for record in self:
            total_discussion = []
            for line in record.particular_id:
                total_discussion.append(line.name)
                discuss = ", ".join(str(x) for x in total_discussion)
                record.discussion = discuss


class JoDemand(models.Model):
    _name = 'demand'
    _description = 'Demand'

    name = fields.Char()


class MeetVistProcess(models.Model):
    _name = 'meet.visit.process'
    _description = 'Meet Visit Process'

    name = fields.Char(required=True, index=True, string="Name")
    followup_progress_id = fields.One2many('follow.up.progress', 'meet_visit_process_id')
    user_ids = fields.Many2many('res.users')
    meeting_minutes_record_id = fields.One2many('meeting.minutes.record', 'meet_visit_process_id')
    appendix_id = fields.One2many('appendix', 'meet_visit_process_id')
    first_demand_item_id = fields.One2many('first.demand.item', 'meet_visit_process_id')
    additional_item_id = fields.One2many('additional.item', 'meet_visit_process_id')
    jo_accept_id = fields.Many2one('jo.acceptance', 'meet_visit_process_id')
    date = fields.Date(default=fields.Date.today(), readonly=True)
    demand_id = fields.Many2one('demand', "Demand")
    partner_id = fields.Many2one('res.partner', related="jo_accept_id.partner_id")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('meet.visit.process') or _('New')
        return super(MeetVistProcess, self).create(vals)

    def open_meeting_minutes(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_core.view_meeting_minutes_record').id

        return {
            'name': _('Meeting Minutes Record'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'meet.visit.process',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}


class JOAcceptance(models.Model):
    _name = 'jo.acceptance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'JO Acceptance'

    name = fields.Char(string="Name")
    client_pic_ids = fields.One2many('client.pic', 'jo_accept_id')
    meet_visit_process_id = fields.One2many('meet.visit.process', 'jo_accept_id')
    internal_pic_ids = fields.Many2many('res.users', string="Internal PIC")
    client_pic_id = fields.Many2one('res.partner', 'Client PIC')
    shop_id = fields.Many2one('shop.list')
    pic_name = fields.Char()
    phone = fields.Char()
    cate_group_id = fields.Many2one('service.category.group', string='Service Group')
    cate_sector_id = fields.Many2one('service.category.sector', string='Service Sector')
    cate_line_id = fields.Many2one('service.category.line', string='Service Line')
    manual_project_name = fields.Char()
    map_link = fields.Char()
    map_photo = fields.Binary()
    project_site = fields.Char('Project Site')
    country_id = fields.Many2one('res.country')
    region = fields.Many2one('customer.region')
    city = fields.Many2one('customer.city')
    township = fields.Many2one('customer.township')
    street = fields.Char('Street')
    ward = fields.Char('Ward')
    land_number = fields.Char('No.')
    site_name = fields.Char('Site name / Building name')
    tower_type = fields.Char('Tower Type')
    tower_no = fields.Char('Tower No')
    floor = fields.Char('Floor')
    order_agreement_id = fields.One2many('jo.order.agreement', 'jo_accept_id')
    add_jo_agreement_id = fields.One2many('addit.jo.agreement', 'jo_accept_id')
    task_id = fields.Many2one('project.task', string="Task")
    project_id = fields.Many2one('project.project', string="Project", required=True)
    partner_id = fields.Many2one('res.partner')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('jo.acceptance') or _('New')
        return super(JOAcceptance, self).create(vals)

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

    @api.onchange('country_id', 'region', 'city', 'township', 'street', 'ward', 'land_number', 'site_name',
                  'tower_type',
                  'tower_no', 'floor')
    def _compute_material_code_name(self):
        project_site = [[lambda: '', lambda: '(' + self.site_name + ')'][self.site_name != False](),
                        self.tower_type or '', self.tower_no or '', self.floor or '',
                        [lambda: '', lambda: ',No.:' + self.land_number][self.land_number != False](), self.street
                        or '', self.ward or '', self.township.name or '', ',', self.city.name or '', ',',
                        self.region.name or '', ',', self.country_id.name or '']
        self.project_site = " ".join(str(site) for site in filter(lambda r: r != '', project_site))

    @api.onchange('cate_group_id')
    def set_service_sector_to(self):
        # self.cate_group_id = False
        self.cate_sector_id = False
        if self.cate_group_id:
            ids = self.env['service.category.sector'].search([('left_id', '=', self.cate_group_id.id)])
            return {
                'domain': {'cate_sector_id': [('id', 'in', ids.ids)], }
            }

    @api.onchange('cate_sector_id')
    def set_service_line_to(self):
        # self.cate_group_id = False
        self.cate_line_id = False
        if self.cate_sector_id:
            ids = self.env['service.category.line'].search([('left_id', '=', self.cate_sector_id.id)])
            return {
                'domain': {'cate_line_id': [('id', 'in', ids.ids)], }
            }


class JoOrderAgreement(models.Model):
    _name = 'jo.order.agreement'
    _description = 'JO Order Agreement'

    date = fields.Date(default=fields.Date.today(), readonly=True)
    agreement_file_upload = fields.Binary()
    jo_accept_id = fields.Many2one('jo.acceptance')


class AdditJoAgreement(models.Model):
    _name = 'addit.jo.agreement'
    _description = 'Addit JO Agreement'

    date = fields.Date(default=fields.Date.today(), readonly=True)
    agreement_file_upload = fields.Binary()
    jo_accept_id = fields.Many2one('jo.acceptance')
