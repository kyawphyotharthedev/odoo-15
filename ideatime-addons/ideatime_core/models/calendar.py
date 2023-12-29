from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    project_id = fields.Many2one('project.project', string="Project")
    employee_id = fields.Many2many('hr.employee', string="Employees",
                                   default=lambda self: self.env['hr.employee'].search([]))
    meeting_type = fields.Selection([
        ('internal', 'Internal Meeting'),
        ('external', 'External Meeting')], default='internal')
    meeting_particular = fields.Char(string="Meeting Particular")
    task_id = fields.Many2one('project.task', string="Project Task")
    calldate = fields.Datetime(string="Call Date")
    meeting_min_type = fields.Selection([
        ('phone', 'Phone Call'),
        ('visit', 'Visit'), ('wechat', 'WeChat'), ('teamviewer', 'Teamviewer'), ('ding', 'Ding Talk')], default='phone',
        string="Meeting Minutes Type")
    location = fields.Text(string="Meeting Location")
    meeting_participant_id = fields.One2many('meeting.participant', 'participant_id')
    meeting_cc_id = fields.One2many('meeting.cc', 'cc_id')
    meeting_topic_id = fields.One2many('meeting.topic', 'topic_id')
    meeting_summary_id = fields.One2many('meeting.summary', 'summary_id')
    meeting_conclusion_id = fields.One2many('meeting.conclusion', 'conclusion_id')
    meeting_action_id = fields.One2many('meeting.action', 'action_id')


class MeetingParticipant(models.Model):
    _name = 'meeting.participant'
    _description = 'Meeting Participant'

    participant_id = fields.Many2one('calendar.event', 'meeting_participant_id')
    model_type = fields.Char(string="Model Type")
    employee_id = fields.Many2one('hr.employee')
    customer_id = fields.Many2one('res.partner')
    supplier_id = fields.Char(string="Supplier")
    thirtparty_id = fields.Char(string="ThirtParty")
    government_id = fields.Char(string="Government")
    participant_name = fields.Char()
    department_id = fields.Many2one('hr.department')
    position = fields.Char(string="Position")


class MeetingCC(models.Model):
    _name = 'meeting.cc'
    _description = 'Meeting CC'

    cc_id = fields.Many2one('calendar.event', 'meeting_cc_id')
    model_type = fields.Char(string="Model Type")
    customer_id = fields.Many2one('res.partner')
    email = fields.Char(string="Email")


class MeetingTopic(models.Model):
    _name = 'meeting.topic'
    _description = 'Meeting Topic'

    topic_id = fields.Many2one('calendar.event', 'meeting_topic_id')
    particular = fields.Char(string="Particular")
    des = fields.Text(string="Description")


class MeetingSummary(models.Model):
    _name = 'meeting.summary'
    _description = 'Meeting Summary'

    summary_id = fields.Many2one('calendar.event', 'meeting_summary_id')
    particular = fields.Char(string="Particular")
    des = fields.Text(string="Description")


class MeetingConclusion(models.Model):
    _name = 'meeting.conclusion'
    _description = 'Meeting Conclusion'

    conclusion_id = fields.Many2one('calendar.event', 'meeting_conclusion_id')
    particular = fields.Char(string="Particular")
    des = fields.Text(string="Description")


class MeetingAction(models.Model):
    _name = 'meeting.action'
    _description = 'Meeting Action'

    action_id = fields.Many2one('calendar.event', 'meeting_action_id')
    task_id = fields.Many2one('project.task')
    res_person = fields.Many2one('res.partner', string="Responsible Person")
    deadline = fields.Datetime(string="Deadline")



