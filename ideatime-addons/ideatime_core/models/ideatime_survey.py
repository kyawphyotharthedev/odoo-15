from odoo import models, fields, api


class IdeaTimeSurvey(models.Model):
    _name = 'ideatime.survey'
    _description = 'IdeaTime Survey'

    name = fields.Char(required=True, index=True, string="Name")
    survey_line_id = fields.One2many('ideatime.survey.line', 'survey_id')
    survey_layout_id = fields.One2many('ideatime.survey.layout.line', 'survey_layout_line_id')
    ideatime_additional_id = fields.One2many('ideatime.additional.information', 'additional_id')
    other_supplementary_id = fields.One2many('other.supplementary.information', 'supplementary_id')
    ideatime_data_resource_id = fields.One2many('ideatime.data.resource', 'data_resource_id')
    ideatime_preparation_process_id = fields.One2many('ideatime.preparation.process', 'preparation_process_id')
    ideatime_design_id = fields.One2many('ideatime.design.resource', 'design_id')
    ideatime_proposal_id = fields.One2many('ideatime.design.proposal', 'proposal_id')
    ideatime_production_id = fields.One2many('ideatime.production', 'production_id')
    ideatime_meeting_additional_id = fields.One2many('ideatime.meeting.additional.information', 'meeting_additional_id')
    ideatime_meeting_supplementary_id = fields.One2many('meeting.supplementary.information', 'meeting_supplementary_id')
    ideatime_investigation_id = fields.One2many('ideatime.basic.investigation', 'investigation_id')
    ideatime_area_id = fields.One2many('ideatime.area', 'area_id')
    partner_id = fields.Many2one('res.partner', required=True)
    employee_id = fields.Many2one("hr.employee")
    product_id = fields.Many2one('product.product')
    project_code = fields.Char(string="Project Code")
    project_survey_id = fields.Many2one('project.project', string="Project", required=True)
    task_survey_id = fields.Many2one('project.task', string="Task", required=True)
    accepted_date = fields.Date(string="Accepted Date")
    survey_requirement = fields.Char(string="Survey Requirement")
    survey_date = fields.Datetime(string="Survey Date")
    maps = fields.Binary(string='Maps')
    design_accepted_date = fields.Date(string="Design Accepted Date")
    item_code = fields.Char(string="Item Code")
    item_name = fields.Char(string="Item Name")
    function = fields.Char(string="Function")
    option = fields.Char(string="Option")
    remark = fields.Char(string="Remark")
    unit = fields.Char(string="Unit")
    summary = fields.Char(string="Summary")
    particular = fields.Char(string="Particular")
    first_meeting = fields.Selection([
        ('ideatime_office', 'Ideatime Office'),
        ('client_office', 'Client Office'),
        ('shop', 'Shop'), ('site', 'Site'), ('phone', 'Phone'), ('other', 'Other')], default='ideatime_office')

    to_know_company = fields.Selection([
        ('facebook', 'Facebook'),
        ('website', 'Website'),
        ('reffered', 'Reffered'), ('offline_media', 'Offline Media'), ('enquiry', 'Enquiry'),
        ('social_net', 'Social  Network'), ('community', 'Community'), ('marketing', 'Marketing')], default='marketing')
    # customer_interest=fields.Text(string="Customer Interest")
    customer_interest = fields.Selection([
        ('sector', 'Service Sector'),
        ('service_line', 'Service Line'),
        ('particular', 'Particular'),
        ('function', 'Function')])

    project_type_id = fields.Many2one('project.type')
    description = fields.Char()

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
    reactive_contact_info_ids = fields.One2many('project.reactive.contact.info', 'survey_id')

    survey_remark = fields.Text('Remark for Survey')

    survey_size = fields.Char('Size')
    survey_qty = fields.Char('Qty')

    survey_measure_rec_ids = fields.One2many('survey.measure.record', 'survey_id')
    basic_investigation_ids = fields.One2many('survey.basic.investigation', 'survey_id')
    site_problems_ids = fields.One2many('survey.site.problems', 'survey_id')

    floor_area = fields.Float('Floor Area', compute="_compute_area")
    wall_area = fields.Float('Wall Area', compute="_compute_area")
    only_wall_area = fields.Float('Wall Area(Door, Window Excluded)', compute="_compute_area")
    door_area = fields.Float('Door Area', compute="_compute_area")
    window_area = fields.Float('Window Area', compute="_compute_area")
    area_calc_list_ids = fields.One2many('survey.area.calc.line', 'survey_id')

    @api.onchange('area_calc_list_ids')
    def _compute_area(self):
        total_floor_area = 0.0
        total_wall_area = 0.0
        total_only_wall_area = 0.0
        total_door_area = 0.0
        total_window_area = 0.0

        for line in self.area_calc_list_ids:
            total_floor_area += line.floor_area
            total_wall_area += line.wall_area
            total_only_wall_area += line.only_wall_area
            total_door_area += line.door_area
            total_window_area += line.window_area

        self.floor_area = total_floor_area
        self.wall_area = total_wall_area
        self.only_wall_area = total_only_wall_area
        self.door_area = total_door_area
        self.window_area = total_window_area

    @api.onchange('city', 'township', 'street', 'ward', 'land_number', 'site_name', 'tower_type', 'tower_no', 'floor')
    def _compute_material_code_name(self):
        project_site = [[lambda: '', lambda: '(' + self.site_name + ')'][self.site_name != False](),
                        self.tower_type or '', self.tower_no or '', self.floor or '',
                        [lambda: '', lambda: 'No.:' + self.land_number][self.land_number != False](), self.street or '',
                        self.ward or '', self.township or '', self.city or '']
        self.project_site = " ".join(str(site) for site in filter(lambda r: r != '', project_site))


class IdeaTimeArea(models.Model):
    _name = "ideatime.area"
    _description = "Area"

    area_id = fields.Many2one('ideatime.survey', 'ideatime_area_id')

    unit = fields.Char(string="Unit")
    qty = fields.Char(string="Qty")
    particular = fields.Char(string="Particular")
    remark = fields.Char(string="Remark")


class IdeaTimeBasicInvestigation(models.Model):
    _name = "ideatime.basic.investigation"
    _description = "Basic Investigation"

    particular = fields.Char(string="Particular")
    des = fields.Char(string="Description")
    situation_analysis = fields.Selection([
        ('normal', 'Normal'),
        ('unormal', 'Unormal'),
        ('blocked', 'Blocked')], default='normal')
    remark = fields.Char(string="Remark")
    investigation_id = fields.Many2one('ideatime.survey', 'ideatime_investigation_id')


class IdeatimeAdditionalInformation(models.Model):
    _name = "ideatime.additional.information"
    _description = "Additional Information"

    additional_id = fields.Many2one('ideatime.survey', 'ideatime_additional_id')
    particular = fields.Char(string="Particular")
    description = fields.Char(string="Description")


class OtherSupplementaryinformation(models.Model):
    _name = 'other.supplementary.information'
    _description = 'Other Supplementary Information'

    supplementary_id = fields.Many2one('ideatime.survey', 'other_supplementary_id')
    particular = fields.Char(string="Particular")
    description = fields.Char(string="Description")


class IdeatimeAdditionalInformationRemark(models.Model):
    _name = "ideatime.meeting.additional.information"
    _description = "Additional Information Remark"
    meeting_additional_id = fields.Many2one('ideatime.survey', 'ideatime_meeting_additional_id')
    particular = fields.Char(string="Particular")
    description = fields.Char(string="Description")


class OtherSupplementaryinformationRemark(models.Model):
    _name = 'meeting.supplementary.information'
    _description = 'Meeting Supplementary Information Remark'

    meeting_supplementary_id = fields.Many2one('ideatime.survey', 'ideatime_meeting_supplementary_id')
    particular = fields.Char(string="Particular")
    description = fields.Char(string="Description")


class IdeaTimeDataResource(models.Model):
    _name = 'ideatime.data.resource'
    _description = 'Data Resource'

    data_resource_id = fields.Many2one('ideatime.survey', 'ideatime_data_resource_id')
    particular = fields.Char(string="Particular")
    remark = fields.Binary(string="Remark")


class IdeaTimePreparationProcess(models.Model):
    _name = 'ideatime.preparation.process'
    _description = 'Preparation Process'

    preparation_process_id = fields.Many2one('ideatime.survey', 'ideatime_preparation_process_id')
    action_step = fields.Char(string="Action Steps")
    deadline = fields.Datetime(string="Deadline")
    resp_person = fields.Char(string="Responsible Person")
    nece_resource = fields.Char(string="Necessary Resources")
    pot_challenge = fields.Char(string="Potential Challenges")
    action_plan = fields.Char(string="Action Plans")
    result = fields.Char(string="Result")
    remark = fields.Char(string="Remark")


class IdeaTimeSurveyLayout(models.Model):
    _name = "ideatime.survey.layout.line"
    _description = "Survey Layout Line"

    survey_layout_line_id = fields.Many2one('ideatime.survey', 'survey_layout_id')
    survey_photo_name = fields.Char(string="Name")
    survey_photo = fields.Binary(string="Photo")


class IdeaTimeSurveyLine(models.Model):
    _name = 'ideatime.survey.line'
    _description = 'Survey Line'

    survey_id = fields.Many2one('ideatime.survey', 'survey_line_id')
    name = fields.Char(string="Name")
    room_photo = fields.Binary(string="Room")
    celling_photo = fields.Binary(string="Celling")
    wall_photo = fields.Binary(string="Wall")
    floor_photo = fields.Binary(string="Floor")
    other_photo = fields.Binary(string="Other")
    area_code = fields.Char(string="Area Code")


class IdeaTimeDesignResource(models.Model):
    _name = 'ideatime.design.resource'
    _description = 'Design Resource'

    item_code = fields.Char(string="Item Code")
    item_name = fields.Char(string="Item Name")
    item_description = fields.Char(string="Item Description")
    item_specification = fields.Char(string="Item Specification")
    item_qty = fields.Char(string="Qty")
    data_info_resource = fields.Char(string="Data Info Resource")
    design_remark = fields.Char(string="Remark")
    design_id = fields.Many2one('ideatime.survey', 'ideatime_design_id')


class IdeaTimeDesignProposal(models.Model):
    _name = 'ideatime.design.proposal'
    _description = 'Design Proposal'

    proposal_particular = fields.Char(string="Particular")
    proposal_accepted_date = fields.Date(string="Accepted Date")
    proposal_date = fields.Date(string="Proposal Date")
    proposal_remark = fields.Char(string="Remark")
    proposal_id = fields.Many2one('ideatime.survey', 'ideatime_proposal_id')


class IdeaTimeProductionData(models.Model):
    _name = 'ideatime.production'
    _description = 'Production Data'

    production_particualar = fields.Binary(string="Particualr")
    production_id = fields.Many2one('ideatime.survey', 'ideatime_production_id')


class ProjectContactInfoParticular(models.Model):
    _name = 'project.contact.particular'
    _description = 'Project Contact Particular'

    name = fields.Char('Name', required=True)


class SurveyMeasureRecord(models.Model):
    _name = 'survey.measure.record'
    _description = 'Survey Measure Record'

    survey_id = fields.Many2one('ideatime.survey')
    ideatime_survey_id = fields.Many2one('ideatime.task.survey')
    particular = fields.Selection([
        ('room', 'Room'),
        ('ball_room', 'Ball Room'),
        ('shop', 'Shop'),
        ('hall', 'Hall'),
        ('toilet', 'Toilet'),
        ('bathroom', 'Bath Room'),
        ('garden', 'Garden'),
        ('...', '...')], string='Particular')
    floor_code = fields.Selection([
        ('3b', '3B'),
        ('2b', '2B'),
        ('1b', '1B'),
        ('g', 'G'),
        ('1f', '1F'),
        ('2f', '2F'),
        ('3f', '3F'),
        ('...', '...')], string='Floor Code')
    area_code = fields.Selection([
        ('a1', 'A1'),
        ('a2', 'A2'),
        ('a3', 'A3'),
        ('...', '...')], string='Area Code')
    view_point = fields.Selection([
        ('over_view', 'Over View'),
        ('right_side_view', 'Right Side View'),
        ('left_side_view', 'Left Side View'),
        ('right_side_wide_view', 'Right Side Wide View'),
        ('left_side_wide_view', 'Left Side Wide View'),
        ('other', 'Other')], string='View Point')
    existing_structure = fields.Binary('Existing Structure')
    existing_photo = fields.Binary('Existing Photo')
    existing_layout_plan = fields.Binary('Existing Layout')
    situation_analysis = fields.Char('Situation Analysis')
    remark = fields.Text('Remark')


class SurveyBasicInvestigation(models.Model):
    _name = 'survey.basic.investigation'
    _description = 'Survey Basic Investigation'

    survey_id = fields.Many2one('ideatime.survey')
    ideatime_survey_id = fields.Many2one('ideatime.task.survey')
    particular = fields.Char()
    description = fields.Char(string="Description")
    situation_analysis = fields.Char(string="Situation Analysis")
    remark = fields.Char(string="Remark")


class ProjectSiteProblems(models.Model):
    _name = 'survey.site.problems'
    _description = 'Survey Site Problems'

    survey_id = fields.Many2one('ideatime.survey')
    ideatime_survey_id = fields.Many2one('ideatime.task.survey')
    particular = fields.Selection([
        ('cable_hinder_impact', 'Cable Hinder Impact'),
        ('surrounding_environment_impact', 'Surrounding environment impact'),
        ('weather_impact', 'Weather impact'),
        ('...', '...')], string='Particular')
    description = fields.Char(string="Description")
    situation_analysis = fields.Char(string="Situation Analysis")
    remark = fields.Char(string="Remark")


class SurveyAreaCalcList(models.Model):
    _name = "survey.area.calc.line"
    _description = "Survey Area Calc Line"

    survey_id = fields.Many2one('ideatime.survey')
    ideatime_survey_id = fields.Many2one('ideatime.task.survey')
    particular = fields.Char(string="Particular", required=True)
    floor_area = fields.Float('Floor Area')
    wall_area = fields.Float('Wall Area')
    only_wall_area = fields.Float('Wall Area(Door, Window Excluded)')
    door_area = fields.Float('Door Area')
    window_area = fields.Float('Window Area')
    item = fields.Float('Item')
    uom_id = fields.Many2one('uom.uom', string='Unit')
    area_code = fields.Many2one('area.code')
    area_type = fields.Many2one('area.type')
    survey_info_line_id = fields.Many2one('survey.info.line')
    info_type = fields.Selection(related='survey_info_line_id.type', readonly=True)

    @api.onchange('wall_area', 'door_area', 'window_area')
    def _wall_area_change(self):
        self.only_wall_area = self.wall_area - (self.door_area + self.window_area)


class ProjectReaciveContactInfo(models.Model):
    _name = "project.reactive.contact.info"
    _description = "Project Reactive Contact Info"

    survey_id = fields.Many2one('ideatime.survey')
    particular_id = fields.Many2one('project.contact.particular', string='Particular', required=True)
    pic_name = fields.Char('PIC Name')
    phone_no = fields.Char('Phone No')
    remark = fields.Char(string="Remark")
