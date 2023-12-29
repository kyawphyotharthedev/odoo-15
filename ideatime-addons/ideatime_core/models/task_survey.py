from odoo import models, fields, api, _


class Appendix(models.Model):
    _name = 'appendix'
    _description = 'Appendix'

    name = fields.Char()
    upload = fields.Binary()
    file_name = fields.Char()
    file_path = fields.Char(string="Url")
    remark = fields.Text()
    survey_task_id = fields.Many2one('ideatime.task.survey')
    meet_visit_process_id = fields.Many2one('meet.visit.process')
    followup_progress_id = fields.Many2one('follow.up.progress')


class OtherPhotoLine(models.Model):
    _name = 'other.photo.line'
    _description = 'Other Photo Line'

    survey_info_line_id = fields.Many2one('survey.info.line')
    other_photo = fields.Binary(string='Sample Photo')
    file_name = fields.Char("File Name")


class Remark(models.Model):
    _name = 'remark.line'
    _description = 'Remark Line'

    description = fields.Text()
    survey_info_line_id = fields.Many2one('survey.info.line')


class Demand(models.Model):
    _name = 'demand.line'
    _description = 'Demand Line'

    particular = fields.Char()
    description = fields.Text()
    survey_info_line_id = fields.Many2one('survey.info.line')

    name = fields.Char()


class AreaType(models.Model):
    _name = 'area.type'
    _description = 'Area Type'

    name = fields.Char()


class AreaCode(models.Model):
    _name = 'area.code'
    _description = 'Area Code'

    name = fields.Char()


class SurveyInfoLine(models.Model):
    _name = 'survey.info.line'
    _description = 'Survey Info Line'

    floor_area = fields.Float('Floor Area', compute="_compute_area", digits=(16, 2))
    wall_area = fields.Float('Wall Area', compute="_compute_area", digits=(16, 2))
    only_wall_area = fields.Float('Wall Area(Door, Window Excluded)', compute="_compute_area", digits=(16, 2))
    door_area = fields.Float('Door Area', compute="_compute_area", digits=(16, 2))
    window_area = fields.Float('Window Area', compute="_compute_area", digits=(16, 2))
    item = fields.Float('Item', compute="_compute_area", digits=(16, 2))
    uom_id = fields.Many2one('uom.uom', string='Uom')
    area_type = fields.Char(compute='_compute_area')
    area_code = fields.Char(compute='_compute_area')
    type = fields.Selection([
        ('area', 'Area'),
        ('item', 'Item')], default="area")
    area_calc_report = fields.Text(compute="_compute_area_cal")
    demand = fields.Char(compute="_compute_demand")
    remark = fields.Text(compute="_compute_remark", string="Remark")
    info = fields.Text()
    survey_info_id = fields.Many2one('survey.info')
    area_calc_line_id = fields.One2many('survey.area.calc.line', 'survey_info_line_id')
    demand_line_id = fields.One2many('demand.line', 'survey_info_line_id')
    remark_id = fields.One2many('remark.line', 'survey_info_line_id', string='Remark Line')
    layout_photo = fields.Binary()
    front_scence_photo = fields.Binary(string="Scence Photo(Front side)")
    left_scence_photo = fields.Binary(string="Scence Photo(Left side)")
    right_scence_photo = fields.Binary(string="Scence Photo(Right side)")
    other_scence_photo = fields.Binary(string="Scence Photo(Other)")
    other_photo_line_ids = fields.One2many('other.photo.line', 'survey_info_line_id')
    unit = fields.Char(compute="_compute_area")
    take_photo = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    wall = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    ceiling = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    floor = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    window = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    bean = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], string="Bean,Column", required=True, default="yes")
    varender = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    piping_system = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], string="Piping System(Celling, Wall Floor)", required=True, default="yes")
    connstanncy_area = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], string="Connstanncy Area(Curb Area)", required=True, default="yes")
    stair_area = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")
    refrence_exit = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], string="Refrence Exit(Toilet, Ground Tank)", required=True, default="yes")
    description = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No need to measure')], required=True, default="yes")

    @api.onchange('floor_area', 'wall_area')
    def _compute_area_cal(self):

        for record in self:
            if record.type == 'area':
                total_area = 'Floor area:' + str(record.floor_area) + ' ' + str(
                    record.unit) + '\n' + 'Wall area:' + str(
                    record.wall_area) + '\n' + 'Wall Area(Door, Window excluded):' + str(
                    record.only_wall_area) + '\n' + 'Door area:' + str(record.door_area) + '\n' + 'Window area:' + str(
                    record.window_area)

                record.area_calc_report = total_area

                print(record.area_calc_report)
            if record.type == 'item':
                total_item = 'Item:' + str(record.item)
                record.area_calc_report = total_item

    @api.onchange('area_calc_line_id')
    def _compute_area(self):

        for record in self:
            total_floor_area = 0.0
            total_wall_area = 0.0
            total_only_wall_area = 0.0
            total_door_area = 0.0
            total_window_area = 0.0
            total_item = 0.0
            total_area_type = []
            total_area_code = []
            unit = ''

            for line in record.area_calc_line_id:
                total_floor_area += line.floor_area
                total_wall_area += line.wall_area
                # total_only_wall_area += line.only_wall_area
                total_door_area += line.door_area
                total_window_area += line.window_area
                total_item += line.item
                total_area_type.append(line.area_type.name)
                area_type = ", ".join(str(x) for x in total_area_type)
                total_area_code.append(line.area_code.name)
                area_code = ", ".join(str(x) for x in total_area_code)
                unit = line.uom_id.name

                record.floor_area = total_floor_area
                record.wall_area = total_wall_area
                record.only_wall_area = total_wall_area - (total_door_area + total_window_area)
                record.door_area = total_door_area
                record.window_area = total_window_area
                record.item = total_item
                record.area_type = area_type
                record.area_code = area_code
                record.unit = unit

    @api.onchange('demand_line_id')
    def _compute_demand(self):

        for record in self:
            total_particular = []
            total_description = []
            total_demand = ''
            for line in record.demand_line_id:
                total_particular.append(line.particular)
                particular = ", ".join(str(x) for x in total_particular)
                total_description.append(line.description)
                description = ", ".join(str(x) for x in total_description)
                total_demand = particular + '/ ' + description

                record.demand = total_demand

    @api.onchange('remark_id')
    def _compute_remark(self):

        for record in self:
            total_remark = []
            for line in record.remark_id:
                total_remark.append(line.description)
                remark = ", ".join(str(x) for x in total_remark)
                record.remark = remark

    def open_area_calc_report(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_core.view_survey_area_calc_line').id

        return {
            'name': _('Area Calaulation Line'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.info.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}


class Floor(models.Model):
    _name = 'floor'
    _description = 'Floor'

    name = fields.Char()


class SurveyInfo(models.Model):
    _name = 'survey.info'
    _description = 'Survey Info'

    name = fields.Char()
    floor = fields.Many2one('floor')
    area_calc = fields.Text(compute="_compute_area_cal")
    survey_task_id = fields.Many2one('ideatime.task.survey')
    survey_info_line_id = fields.One2many('survey.info.line', 'survey_info_id')
    floor_area = fields.Float('Floor Area', compute="_compute_area", digits=(16, 2))
    wall_area = fields.Float('Wall Area', compute="_compute_area", digits=(16, 2))
    only_wall_area = fields.Float('Wall Area(Door, Window Excluded)', compute="_compute_area", digits=(16, 2))
    door_area = fields.Float('Door Area', compute="_compute_area", digits=(16, 2))
    window_area = fields.Float('Window Area', compute="_compute_area", digits=(16, 2))
    item = fields.Float('Item', compute="_compute_area", digits=(16, 2))
    unit = fields.Char(related="survey_info_line_id.unit")
    layout_photo = fields.Binary()
    front_scence_photo = fields.Binary(string="Scence Photo(Front side)")
    left_scence_photo = fields.Binary(string="Scence Photo(Left side)")
    right_scence_photo = fields.Binary(string="Scence Photo(Right side)")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('survey.info') or _('New')
        return super(SurveyInfo, self).create(vals)

    @api.onchange('survey_info_line_id')
    def _compute_area_cal(self):

        for record in self:
            floor_area = 0.0
            wall_area = 0.0
            only_wall_area = 0.0
            door_area = 0.0
            window_area = 0.0
            item = 0.0
            for line in record.survey_info_line_id:
                # if line.type=='area':
                floor_area += line.floor_area
                wall_area += line.wall_area
                only_wall_area += line.only_wall_area
                window_area += line.window_area
                item = line.item
                total_area_calc = 'Floor area:' + str(floor_area) + str(record.unit) + '\n' + 'Wall area:' + str(
                    wall_area) + '\n' + 'Door area:' + str(
                    door_area) + '\n' + 'Wall area(Window, Door excluded):' + str(
                    only_wall_area) + '\n' + 'Window area:' + str(window_area) + '\n' + 'Item:' + str(item)
                record.area_calc = total_area_calc

    @api.onchange('survey_info_line_id')
    def _compute_area(self):
        for record in self:

            for line in record.survey_info_line_id:
                if line.type == 'area':
                    record.floor_area += line.floor_area
                    record.wall_area += line.wall_area
                    record.only_wall_area += line.only_wall_area
                    record.door_area += line.door_area
                    record.window_area += line.window_area
                if line.type == 'item':
                    record.item += line.item

    def open_survey_info(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_core.view_survey_info_line').id

        return {
            'name': _('Survey Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.info',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}


class Building(models.Model):
    _name = 'building.type'
    _description = 'Building Type'

    name = fields.Char()


class IdeaTimeSurvey(models.Model):
    _name = 'ideatime.task.survey'
    _description = 'IdeaTime Survey'

    name = fields.Char(index=True, string="Name")
    task_survey_id = fields.Many2one('project.task', string="Task")
    project_id = fields.Many2one('project.project', string="Project")
    accepted_date = fields.Date(string="Accepted Date")
    survey_requirement = fields.Char(string="Survey Requirement")
    survey_date = fields.Datetime(string="Survey Date", required=True)
    maps = fields.Binary(string='Maps')

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
    floor_area = fields.Float('Floor Area', compute="_compute_area", digits=(16, 2))
    wall_area = fields.Float('Wall Area', compute="_compute_area", digits=(16, 2))
    only_wall_area = fields.Float('Wall Area(Door, Window Excluded)', compute="_compute_area", digits=(16, 2))
    door_area = fields.Float('Door Area', compute="_compute_area", digits=(16, 2))
    window_area = fields.Float('Window Area', compute="_compute_area", digits=(16, 2))
    survey_measure_rec_ids = fields.One2many('survey.measure.record', 'ideatime_survey_id')
    area_calc_list_ids = fields.One2many('survey.area.calc.line', 'ideatime_survey_id')
    basic_investigation_ids = fields.One2many('survey.basic.investigation', 'ideatime_survey_id')
    site_problems_ids = fields.One2many('survey.site.problems', 'ideatime_survey_id')
    map_link = fields.Char()
    client_pic = fields.Many2one('res.partner', required=True)
    survey_pic = fields.Many2one('res.partner', required=True)
    shop_name = fields.Char(required=True)
    implement_site_pic_name = fields.Char('res.partner', required=True)

    phoneno = fields.Char()
    building_type = fields.Many2one('building.type')
    structural_state = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Sturctural State', required=True)
    dismantle_work = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    site_preparation_work = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    working_period = fields.Selection([
        ('day', 'Day'),
        ('night', 'Night'), ('day/night', 'Day/Night')], required=True)
    electiricity_supply = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    water_supply = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    permission_process = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    accommodation = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    material_purchase = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    material_transporaion = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    delivery = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    passenger_transporation = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    surrounding_env_impact = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    building_water_leakage = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    cable_hinder_impact = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    const_team_impact = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)
    weather_rain_impact = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], required=True)

    implement_site_photo = fields.Binary()
    item_area = fields.Float(compute="_compute_area", digits=(16, 2))
    survey_info_id = fields.One2many('survey.info', 'survey_task_id')
    unit = fields.Char(related="survey_info_id.unit")
    appendix_id = fields.One2many('appendix', 'survey_task_id')
    jo_accept_id = fields.Many2one('jo.acceptance')

    @api.onchange('jo_accept_id')
    def onchange_jo_accept_id(self):
        result = {}
        if not self.jo_accept_id:
            return result
        self.map_link = self.jo_accept_id.map_link
        self.maps = self.jo_accept_id.map_photo
        self.project_site = self.jo_accept_id.project_site
        self.country_id = self.jo_accept_id.country_id
        self.region = self.jo_accept_id.region
        self.city = self.jo_accept_id.city
        self.township = self.jo_accept_id.township
        self.street = self.jo_accept_id.street
        self.ward = self.jo_accept_id.ward
        self.land_number = self.jo_accept_id.land_number
        self.site_name = self.jo_accept_id.site_name
        self.tower_type = self.jo_accept_id.tower_type
        self.tower_no = self.jo_accept_id.tower_no
        self.floor = self.jo_accept_id.floor

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ideatime.task.survey') or _('New')
        return super(IdeaTimeSurvey, self).create(vals)

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

    @api.onchange('survey_info_id')
    def _compute_area(self):
        for record in self:
            record.floor_area = 0
            record.wall_area = 0
            record.only_wall_area = 0
            record.door_area = 0
            record.window_area = 0
            record.item_area = 0
            for line in record.survey_info_id:
                record.floor_area += line.floor_area
                record.wall_area += line.wall_area
                record.only_wall_area += line.only_wall_area
                record.door_area += line.door_area
                record.window_area += line.window_area
                record.item_area += line.item
