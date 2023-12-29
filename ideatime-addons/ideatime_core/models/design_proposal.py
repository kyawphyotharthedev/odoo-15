from odoo import models, fields, api, _


class LightingDetail(models.Model):
    _name = 'lighting.details'
    _description = 'Lighting Details'

    title = fields.Char()
    lighting_template = fields.Char()
    description = fields.Text()
    product_info = fields.Char()
    sample_photo = fields.Binary()
    lighting_info_id = fields.Many2one('lighting.info')


class LightingInfoLine(models.Model):
    _name = 'lighting.info.line'
    _description = 'Lighting Info Line'

    label_no = fields.Char()
    label_color = fields.Selection([
        ('red', 'Red'),
        ('green', 'Green'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('greenyellow', 'GreenYellow'),
        ('navajowhite', 'NavajoWhite'), ('cadetblue', 'CadetBlue'), ('darkblue', 'Darkblue'), ('skyblue', 'SkyBlue'),
        ('darkgray', 'DarkGray'), ('royalblue', 'RoyalBlue')], default="red")
    title = fields.Char()
    description = fields.Char()
    lighting_info_id = fields.Many2one('lighting.info')


class BasicMaterial(models.Model):
    _name = 'basic.material'
    _description = 'Basic Material'

    label_no = fields.Char()
    label_color = fields.Selection([
        ('red', 'Red'),
        ('green', 'Green'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('greenyellow', 'GreenYellow'),
        ('navajowhite', 'NavajoWhite'), ('cadetblue', 'CadetBlue'), ('darkblue', 'Darkblue'), ('skyblue', 'SkyBlue'),
        ('darkgray', 'DarkGray'), ('royalblue', 'RoyalBlue')], default="red")
    specification = fields.Char()
    particular = fields.Char()
    material_info_id = fields.Many2one('material.info')


class DecorativeMaterial(models.Model):
    _name = 'decorative.material'
    _description = 'Decorative Material'

    label_no = fields.Char()
    label_color = fields.Selection([
        ('red', 'Red'),
        ('green', 'Green'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('greenyellow', 'GreenYellow'),
        ('navajowhite', 'NavajoWhite'), ('cadetblue', 'CadetBlue'), ('darkblue', 'Darkblue'), ('skyblue', 'SkyBlue'),
        ('darkgray', 'DarkGray'), ('royalblue', 'RoyalBlue')], default="red")
    title = fields.Char()
    description = fields.Text()
    specification = fields.Char()
    product_info = fields.Char()
    particular = fields.Char()
    sample_photo = fields.Binary()
    material_info_id = fields.Many2one('material.info')


class LightingInfo(models.Model):
    _name = 'lighting.info'
    _description = 'Lighting Info'

    particular = fields.Char()
    remark = fields.Text()
    sample_photo = fields.Binary()
    product_info_id = fields.Many2one('product.info')
    lighting_info_line_id = fields.One2many('lighting.info.line', 'lighting_info_id')
    lighting_details_id = fields.One2many('lighting.details', 'lighting_info_id')


class MaterialInfo(models.Model):
    _name = 'material.info'
    _description = 'Material Info'

    particular = fields.Char()
    remark = fields.Text()
    sample_photo = fields.Binary()
    product_info_id = fields.Many2one('product.info')
    decorative_material_id = fields.One2many('decorative.material', 'material_info_id')
    basic_material_id = fields.One2many('basic.material', 'material_info_id')


class FixtureDesignInfo(models.Model):
    _name = 'fixture.des.info.line'
    _description = 'Fixture Design Info Line'

    no = fields.Char()
    label_color = fields.Selection([
        ('red', 'Red'),
        ('green', 'Green'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('greenyellow', 'GreenYellow'),
        ('navajowhite', 'NavajoWhite'), ('cadetblue', 'CadetBlue'), ('darkblue', 'Darkblue'), ('skyblue', 'SkyBlue'),
        ('darkgray', 'DarkGray'), ('royalblue', 'RoyalBlue')], default="red")
    particular = fields.Char()
    fixture_design_des_id = fields.Many2one('fixture.design.description')


class DesignDesInfo(models.Model):
    _name = 'design.des.info'
    _description = 'Design Des Info'

    no = fields.Char()
    label_color = fields.Selection([
        ('red', 'Red'),
        ('green', 'Green'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('greenyellow', 'GreenYellow'),
        ('navajowhite', 'NavajoWhite'), ('cadetblue', 'CadetBlue'), ('darkblue', 'Darkblue'), ('skyblue', 'SkyBlue'),
        ('darkgray', 'DarkGray'), ('royalblue', 'RoyalBlue')], default="red")
    particular = fields.Char()
    design_des_id = fields.Many2one('design.description')


class DesignRequirement(models.Model):
    _name = 'design.requirement'
    _description = 'Design Requirement'

    particular = fields.Char()
    description = fields.Text()
    design_concept_id = fields.Many2one('design.concept')


class ClientDesign(models.Model):
    _name = 'client.design'
    _description = 'Client Design'

    business_type = fields.Char()
    store_type = fields.Char()
    store_format = fields.Char()
    appendix_upload = fields.Binary(string="Appendix(Upload)")
    appendix_url = fields.Char(string="Appendix(Url)")
    design_concept_id = fields.Many2one('design.concept')


class UniqueDesign(models.Model):
    _name = 'unique.design'
    _description = 'Unique Design'

    business_type = fields.Char()
    store_type = fields.Char()
    design_theme = fields.Char()
    design_style = fields.Char()
    appendix = fields.Binary(string="Appendix(Upload)")
    design_concept_id = fields.Many2one('design.concept')


class InformationDesign(models.Model):
    _name = 'information.design'
    _description = 'Information Design'

    no = fields.Char()
    label_color = fields.Selection([
        ('red', 'Red'),
        ('green', 'Green'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('greenyellow', 'GreenYellow'),
        ('navajowhite', 'NavajoWhite'), ('cadetblue', 'CadetBlue'), ('darkblue', 'Darkblue'), ('skyblue', 'SkyBlue'),
        ('darkgray', 'DarkGray'), ('royalblue', 'RoyalBlue')], default="red")
    zone_design = fields.Binary()
    zone_name = fields.Char()
    product_id = fields.Many2one('product.product', string="Item name")
    item_code = fields.Char()
    sample_photo = fields.Binary(string="Item Sample Photo")
    remark = fields.Text()
    design = fields.Binary()
    upload = fields.Binary()
    url = fields.Char()
    appendix_pro_info_id = fields.Many2one('appendix.production.info')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.item_code = self.product_id.barcode
        self.sample_photo = self.product_id.image_medium


class Defination(models.Model):
    _name = 'defination'
    _description = 'Defination'

    particular = fields.Char()
    description = fields.Text()
    store_format_id = fields.Many2one('store.format')


class StoreformatDef(models.Model):
    _name = 'store.format.def'
    _description = 'Store Format Def'

    particular = fields.Char()
    description = fields.Text()
    store_format_id = fields.Many2one('store.format')


class ProductInfo(models.Model):
    _name = 'product.info'
    _description = 'Product Info'

    particular = fields.Char()
    design = fields.Binary()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')
    design = fields.Binary()
    product_size = fields.Binary()
    details_drawing = fields.Binary()
    material_info_id = fields.One2many('material.info', 'product_info_id')
    lighting_info_id = fields.One2many('lighting.info', 'product_info_id')


class WorkingDrawing(models.Model):
    _name = 'working.drawing'
    _description = 'Working Drawing'

    particular = fields.Char()
    design = fields.Binary()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')


class FixtureDesignDescription(models.Model):
    _name = 'fixture.design.description'
    _description = 'Fixture Design Description'

    particular = fields.Char(compute="_compute_particular")
    description = fields.Text()
    design = fields.Binary()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')
    fix_design_info_line_id = fields.One2many('fixture.des.info.line', 'fixture_design_des_id')
    design = fields.Binary()
    Layout_view = fields.Binary()

    @api.onchange('particular')
    def _compute_particular(self):

        for record in self:
            total_particular = []
            for line in record.fix_design_info_line_id:
                total_particular.append(line.particular)
                particular = ", ".join(str(x) for x in total_particular)
                record.particular = particular


class DesignDescription(models.Model):
    _name = 'design.description'
    _description = 'Design Description'

    particular = fields.Char(compute="_compute_particular")
    description = fields.Text()
    design = fields.Binary()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')
    design_des_info_id = fields.One2many('design.des.info', 'design_des_id')
    design = fields.Binary()

    @api.onchange('particular')
    def _compute_particular(self):

        for record in self:
            total_particular = []
            for line in record.design_des_info_id:
                total_particular.append(line.particular)
                particular = ", ".join(str(x) for x in total_particular)
                record.particular = particular


class DesignView(models.Model):
    _name = 'design.view'
    _description = 'Design View'

    particular = fields.Char()
    design = fields.Binary()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')


class DesignConcept(models.Model):
    _name = 'design.concept'
    _description = 'Design Concept'

    date = fields.Date()
    particular = fields.Char()
    business_type = fields.Char(compute="_compute_business_type")
    store_type = fields.Char(compute="_compute_store_type")
    design_req = fields.Char(compute="_compute_design_req")
    submit_date = fields.Date()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')
    unique_design_id = fields.One2many('unique.design', 'design_concept_id')
    client_design_id = fields.One2many('client.design', 'design_concept_id')
    design_req_id = fields.One2many('design.requirement', 'design_concept_id')

    @api.onchange('unique_design_id', ' client_design_id')
    def _compute_business_type(self):
        for record in self:
            total_business_type1 = []
            total_business_type2 = []
            total_business_type = ''
            for line1 in record.unique_design_id:
                total_business_type1.append(line1.business_type)
            for line2 in record.client_design_id:
                total_business_type2.append(line2.business_type)
                business_type1 = ", ".join(str(x) for x in total_business_type1)
                business_type2 = ", ".join(str(x) for x in total_business_type2)
                record.business_type = business_type1 + '/ ' + business_type2

    @api.onchange('unique_design_id', ' client_design_id')
    def _compute_store_type(self):
        for record in self:
            total_store_type1 = []
            total_store_type2 = []
            total_store_type = ''
            for line1 in record.unique_design_id:
                total_store_type1.append(line1.store_type)
            for line2 in record.client_design_id:
                total_store_type1.append(line2.store_type)
                store_type1 = ", ".join(str(x) for x in total_store_type1)
                store_type2 = ", ".join(str(x) for x in total_store_type2)
                record.store_type = store_type1
                # record.store_type=total_store_type

    @api.onchange('design_req_id')
    def _compute_design_req(self):

        for record in self:
            total_particular = []
            total_description = []
            total_design_req = ''
            for line in record.design_req_id:
                total_particular.append(line.particular)
                particular = ", ".join(str(x) for x in total_particular)
                total_description.append(line.description)
                description = ", ".join(str(x) for x in total_description)
                total_design_req = particular + '/ ' + description

                record.design_req = total_design_req


class PreliminaryDesign(models.Model):
    _name = 'preliminary.design'
    _description = 'Preliminary Design'

    date = fields.Date()
    particular = fields.Char()
    design_layout = fields.Char(string="Design Layout Distribution")
    submit_date = fields.Date()
    outdoor_env_system_id = fields.Many2one('outdoor.env.system')


class AppendixInfo(models.Model):
    _name = 'appendix.info'
    _description = 'Appendix Info'

    particular = fields.Char()
    remark = fields.Text()
    upload = fields.Binary()
    url = fields.Char()
    design_proposal_id = fields.Many2one('design.proposal')


class AppendixProInfo(models.Model):
    _name = 'appendix.production.info'
    _description = 'Appendix Production Info'

    name = fields.Char(required=True, index=True, string="Name")
    particular = fields.Char()
    remark = fields.Text()
    overview = fields.Binary()
    design_proposal_id = fields.Many2one('design.proposal')
    overview_photo = fields.Binary()
    information_design_id = fields.One2many('information.design', 'appendix_pro_info_id')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('appendix.production.info') or _('New')
        return super(AppendixProInfo, self).create(vals)

    def open_appendix(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_project.view_appendix').id

        return {
            'name': _('Store Format'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'appendix.production.info',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}


class DesignStoreFormat(models.Model):
    _name = 'design.store.format'
    _description = 'Design Store Format'

    type = fields.Char()
    description = fields.Text()
    design_format1 = fields.Binary()
    design_format2 = fields.Binary()
    design_format3 = fields.Binary()
    design_proposal_id = fields.Many2one('design.proposal')


class StoreFormat(models.Model):
    _name = 'store.format'
    _description = 'Store Format'

    name = fields.Char(required=True, index=True, string="Name")
    type = fields.Char()
    design = fields.Binary()
    defination = fields.Char()
    design_proposal_id = fields.Many2one('design.proposal')
    design_photo = fields.Binary()
    store_format_def_id = fields.One2many('store.format.def', 'store_format_id')
    defination_id = fields.One2many('defination', 'store_format_id')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('store.format') or _('New')
        return super(StoreFormat, self).create(vals)

    def open_store_format(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_project.view_store_format').id

        return {
            'name': _('Store Format'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'store.format',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}


class OutdoorEnv(models.Model):
    _name = 'outdoor.env.system'
    _description = 'Outdoor Env System'

    name = fields.Char(required=True, index=True, string="Name")

    date = fields.Date(default=fields.Date.today())
    particular = fields.Char()
    pre_demand = fields.Char(string="Design Preparation Demand")
    submit_date = fields.Date()
    design_proposal_id = fields.Many2one('design.proposal')
    design_concept_id = fields.One2many('design.concept', 'outdoor_env_system_id')
    preliminary_design_id = fields.One2many('preliminary.design', 'outdoor_env_system_id')
    design_preparation_demand = fields.Selection([
        ('view_design', 'View Design'),
        ('product', 'Product Information'), ('working', 'Working Drawing')], default="view_design")
    design_layout = fields.Binary()
    design_view_id = fields.One2many('design.view', 'outdoor_env_system_id')
    design_description_id = fields.One2many('design.description', 'outdoor_env_system_id')
    fixture_design_id = fields.One2many('fixture.design.description', 'outdoor_env_system_id')
    working_drawing_id = fields.One2many('working.drawing', 'outdoor_env_system_id')
    product_info_id = fields.One2many('product.info', 'outdoor_env_system_id')
    area_code = fields.Many2one('area.code')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('outdoor.env.system') or _('New')
        print(vals['name'])
        return super(OutdoorEnv, self).create(vals)

    def open_preliminary_docking(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_project.view_outdoor_env_system').id

        return {
            'name': _('Design Concept'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'outdoor.env.system',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}


class Explainsion(models.Model):
    _name = 'design.explainsion'
    _description = 'Design Explainsion'

    name = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class Maintain(models.Model):
    _name = 'design.maintain'
    _description = 'Design Maintain'

    name = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class UseDesign(models.Model):
    _name = 'use.design'
    _description = 'Use Design'

    particular = fields.Char()
    description = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class ScopeApplication(models.Model):
    _name = 'scope.application'
    _description = 'Scope Application'

    name = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class MakingProcess(models.Model):
    _name = 'making.process'
    _description = 'Making Process'

    name = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class DesignIdeas(models.Model):
    _name = 'design.ideas'
    _description = 'Design Ideas'

    particular = fields.Char()
    description = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class Objective(models.Model):
    _name = 'objective'
    _description = 'Objective'

    particular = fields.Char()
    description = fields.Text()
    design_proposal_id = fields.Many2one('design.proposal')


class DesignProposal(models.Model):
    _name = 'design.proposal'
    _description = 'Design Proposal'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    task_id = fields.Many2one('project.task', string="Task", required=True)
    appendix_info_id = fields.One2many('appendix.info', 'design_proposal_id')
    appendix_pro_info_id = fields.One2many('appendix.production.info', 'design_proposal_id')
    design_store_format_id = fields.One2many('design.store.format', 'design_proposal_id')
    store_format_id = fields.One2many('store.format', 'design_proposal_id')
    outdoor_env_system_id = fields.One2many('outdoor.env.system', 'design_proposal_id')
    explansion_id = fields.One2many('design.explainsion', 'design_proposal_id')
    maintain_id = fields.One2many('design.maintain', 'design_proposal_id')
    use_design_ids = fields.One2many('use.design', 'design_proposal_id')

    scope_application_id = fields.One2many('scope.application', 'design_proposal_id')
    making_process_id = fields.One2many('making.process', 'design_proposal_id')
    design_ideas_ids = fields.One2many('design.ideas', 'design_proposal_id')
    particular_id = fields.One2many('particular.line', 'design_proposal_id')
    objective_id = fields.One2many('objective', 'design_proposal_id')

    name = fields.Char(required=True, index=True, string="Name")
    internal_pic_ids = fields.Many2many('res.users')
    particular = fields.Char()
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
    overview_design = fields.Binary()
    cover_design = fields.Binary()
    intro_design = fields.Binary()
    design_overview = fields.Binary()
    design_summary = fields.Binary()
    particular = fields.Binary()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('design.proposal') or _('New')
        print(vals['name'])
        return super(DesignProposal, self).create(vals)

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
