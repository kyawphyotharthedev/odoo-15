from odoo import models, fields


class BasicOfficeSkill(models.Model):
    _name = "office.skill"
    _description = "Office Skill"

    name = fields.Char(string="Office Skill")


class LanguageSkill(models.Model):
    _name = "language.skill"
    _description = "Language Skill"

    name = fields.Char(string="Language Skill")


class Education(models.Model):
    _name = 'education'
    _description = "Part 2. Education"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    name_of_scu = fields.Char(string="Name of School/College/University")
    location_of_scu = fields.Char(string="Location of School/College/University")
    major = fields.Char(string="Major")
    academic_dd = fields.Char(string="Academic Degree/ Diploma")
    education_id = fields.Many2one('hr.employee', string="Education ID")


class Training(models.Model):
    _name = 'training'
    _description = "Part 3. Training "

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    training_institution = fields.Char(string="Training Institution")
    training_place = fields.Char(string="Training Place")
    training_course = fields.Char(string="Training Course")
    certificate = fields.Char(string="Certificate")
    training_id = fields.Many2one('hr.employee', string="Training ID")


class WorkExperience(models.Model):
    _name = 'work.experience'
    _description = "Part 4. Work Experience"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    name_of_company = fields.Char(string="Name of Company")
    position = fields.Char(string="Position")
    main_responsibilities = fields.Text(string="Main Responsibilities")
    reason_for_registration = fields.Text(string="Reasons for Resignation")
    work_experience_id = fields.Many2one('hr.employee', string="Work experience ID")


class PCHSAssessment(models.Model):
    _name = 'pchs.assessment'
    _description = "Part 5. Personality/Characters/Hobbies/Self Assessment"

    personality_characters = fields.Text(string="Personality/ Characters")
    hobbies = fields.Text(string="Hobbies")
    self_assessment = fields.Text(string="Self Assessment")
    pchs_assessment_id = fields.Many2one('hr.employee', string="PCHS assessment ID")


class FamilyData(models.Model):
    _name = 'family.data'
    _description = "Part 6. Family Data"

    marital_status = fields.Selection([
        ('single', 'SINGLE'),
        ('married', 'MARRIED'),
        ('others', 'OTHERS')
    ], string="Marital Status", default='single')
    spouse_name = fields.Char(string="Spouse Name")
    spouse_nrc_no = fields.Char(string="Spouse NRC No.")
    spouse_occupation = fields.Text(string="Spouse Occupation")
    general_information_of_children = fields.Text(string="General Information of Children")
    emergency_contact = fields.Char(string="Emergency Contact")
    family_data_id = fields.Many2one('hr.employee', string="Family data ID")


class BOSHSkill(models.Model):
    _name = 'bosh.skill'
    _description = "Part 7.Basic Office Software/Hardware Skill"

    name = fields.Many2one('office.skill', string="Name")
    knowledge = fields.Selection([
        ('level0', 'Level0'),
        ('level1', 'Level1'),
        ('level2', 'Level2'),
        ('level3', 'Level3')
    ], string="Knowledge", default='level0')
    skill = fields.Selection([
        ('level0', 'Level0'),
        ('level1', 'Level1'),
        ('level2', 'Level2'),
        ('level3', 'Level3')
    ], string="Skill", default='level0')
    bosh_skill_id = fields.Many2one('hr.employee', string="BOSH skill ID")


class Language4Skills(models.Model):
    _name = 'language.4skills'
    _description = "Part 8. Languages ( 4 Skills )"

    name = fields.Many2one('language.skill', string="Name")
    speaking = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string="SPEAKING", default='good')
    reading = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string="READING", default='good')
    writing = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string="WRITING", default='good')
    language_4skills_id = fields.Many2one('hr.employee', string="Language 4 skills ID")


class SpecialitySkillAssessment(models.Model):
    _name = 'speciality.skill.assessment'
    _description = "Part 7.Specility Skill Assessment"

    business_skill = fields.Text(string="Business Skill")
    knowledge = fields.Selection([
        ('level0', 'Level0'),
        ('level1', 'Level1'),
        ('level2', 'Level2'),
        ('level3', 'Level3')
    ], string="Knowledge", default='level0')
    skill = fields.Selection([
        ('level0', 'Level0'),
        ('level1', 'Level1'),
        ('level2', 'level2'),
        ('level3', 'level3')
    ], string="Skill", default='level0')
    speciality_skill_assessment_id = fields.Many2one('hr.employee', string="Speciality skill assessment ID)")


class EmployeeHistory(models.Model):
    _name = 'employee.history'
    _description = "Part 8.Employee History"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    position = fields.Char(string="Position")
    location = fields.Char(string="Location")
    main_responsibility = fields.Text(string="Main Responsibilities")
    employee_history_id = fields.Many2one('hr.employee', string="Employee history ID")


class AppraisalRecord(models.Model):
    _name = 'appraisal.record'
    _description = "Part 9.APPRAISAL RECORD"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    appraisal_result = fields.Text(string="Appraisal Result")
    supervisor_remark = fields.Text(string="Supervisor Remark")
    appraisal_record_id = fields.Many2one('hr.employee', string="Appraisal record ID")


class PerformanceManagementRecord(models.Model):
    _name = 'performance.management.record'
    _description = "Part 10.PERFORMANCE MANAGEMENT RECORD"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    position_responsibilities = fields.Text(string="Fulfillment of Position Responsibilities")
    extra_contribution = fields.Text(string="Extra Contribution")
    detail_work_achievements = fields.Text(string="Detail Work Achievements")
    performance_management_record_id = fields.Many2one('hr.employee', string="Performance management record ID")


class EmployeeSelfAssessmentManagementRecord(models.Model):
    _name = 'employee.self.assessment.management.record'
    _description = "Part 11.EMPLOYEES SELF-ASSESSMENT RECORD ( Result Base )"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    position_responsibilities = fields.Text(string="Fulfillment of Position Responsibilities")
    extra_contribution = fields.Text(string="Extra Contribution")
    self_improvement_plan = fields.Text(string="Self Improvement Plan")
    employee_self_assessment_management_record_id = fields.Many2one('hr.employee', string="Employee self assessment")


class EmployeeViolationRecord(models.Model):
    _name = 'employee.violation.record'
    _description = "Part 12.EMPLOYESS VIOLATION RECORD"

    time_from = fields.Date(string="Time From")
    time_to = fields.Date(string="Time To")
    case_detail = fields.Text(string="Case Detail")
    penalties = fields.Text(string="Penalties")
    follow_up_result = fields.Text(string="Follow up Result")
    employee_violation_record_id = fields.Many2one('hr.employee', string="Employee violation record ID")
