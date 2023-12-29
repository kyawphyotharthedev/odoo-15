from odoo import models, fields, api


class EducationInherit(models.Model):
    _inherit = 'hr.employee'

    employee_id = fields.Char(string="Employee ID")
    education_lines = fields.One2many('education', 'education_id', string="Education lines")
    training_lines = fields.One2many('training', 'training_id', string="Training lines")
    work_experience_lines = fields.One2many('work.experience', 'work_experience_id', string="Work experience lines")
    pchs_assessment_lines = fields.One2many('pchs.assessment', 'pchs_assessment_id', string="PCHS assessment lines")
    family_data_lines = fields.One2many('family.data', 'family_data_id', string="Family data lines")
    bosh_skill_lines = fields.One2many('bosh.skill', 'bosh_skill_id', string="BOSH skill lines")
    language_4skills_lines = fields.One2many('language.4skills', 'language_4skills_id',
                                             string="Language 4 skills lines")
    speciality_skill_assessment_lines = fields.One2many('speciality.skill.assessment',
                                                        'speciality_skill_assessment_id',
                                                        string="Speciality skill assessment lines")
    employee_history_lines = fields.One2many('employee.history', 'employee_history_id', string="Employee history lines")
    appraisal_record_lines = fields.One2many('appraisal.record', 'appraisal_record_id', string="Appraisal record lines")
    performance_management_record_lines = fields.One2many('performance.management.record',
                                                          'performance_management_record_id', string="Performance "
                                                                                                     "management "
                                                                                                     "record lines")
    employee_self_assessment_management_record_lines = fields.One2many('employee.self.assessment.management.record',
                                                                       'employee_self_assessment_management_record_id',
                                                                       string="Employee self assessment record lines")
    employee_violation_record_lines = fields.One2many('employee.violation.record', 'employee_violation_record_id',
                                                      string="Employee violation record lines")

    join_date = fields.Date(string="Join Date")
    current_position = fields.Char(string="Current Position")
    father_name = fields.Char(string="Father Name")
    religion = fields.Char(string="Religion")
    contact_number = fields.Char(string="Contact Number")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
