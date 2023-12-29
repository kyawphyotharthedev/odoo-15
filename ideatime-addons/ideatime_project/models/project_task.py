# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_subtask(self):
        action = self.env["ir.actions.actions"]._for_xml_id('project.project_task_action_sub_task')
        ctx = self.env.context.copy()
        ctx.update({
            'default_parent_id': self.id,
            'default_project_id': self.env.context.get('project_id', self.project_id.id),
            'default_name': self.env.context.get('name', self.name) + ':',
            'default_partner_id': self.env.context.get('partner_id', self.partner_id.id),
            'default_action_step_id': self.env.context.get('action_step_id', self.action_step_id.id),
            'search_default_project_id': self.env.context.get('project_id', self.project_id.id),

        })
        action['context'] = ctx
        action['domain'] = [('id', 'child_of', self.id), ('id', '!=', self.id)]
        return action

    @api.depends('child_ids')
    def checklist_progress(self):
        for record in self:
            record.checklist_progress = 0
            total_task = len(record.child_ids)
            get_task = record.search([('parent_id', 'in', record.ids)])
            total_done = 0
            for task in get_task:

                if task.parent_id and task.stage_id.stage_state == 'done':
                    total_done += 1
            if total_task != 0:
                record.checklist_progress = (total_done * 100) / total_task

    checklist_progress = fields.Float(compute=checklist_progress, string='Progress', store=False, recompute=True,
                                      default=0.0)
    action_step_id = fields.Many2one('action.plan', string="Action step", required=True)

    @api.onchange('stage_id')
    def _on_stage_change(self):
        if self.stage_id.stage_state == 'done':
            for sub_task in self.child_ids:
                if sub_task.stage_id.stage_state not in ('done', 'cancel'):
                    raise UserError(_('You Should Done Sub Tasks First'))

    def _compute_attached_docs_count(self):
        attachment = self.env['ir.attachment']
        for record in self:
            record.doc_count = attachment.search_count([
                ('res_model', '=', 'project.task'), ('res_id', '=', record.id),

            ])

    def _compute_department(self):
        for record in self:
            record.update({'departmant_id': record.env.user.employee_ids.department_id})

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [('res_model', '=', self._name)],
                                     auto_join=True, string='Attachments')
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

    priority = fields.Selection(selection_add=[
        ('0', 'Start'),
        ('1', 'Bad'),
        ('2', 'Normal'),
        ('3', 'Good'),
        ('4', 'Excellent'),
    ], default='0', index=True, string="Priority")
    departmant_id = fields.Many2one('hr.department', compute='_compute_department')
    meeting_ids = fields.One2many('calendar.event', 'task_id', string='Meetings', copy=False)
    meeting_count = fields.Integer("# Meetings", compute='_compute_meeting_count')

    necessary_resources = fields.Html(string='Necessary Resources')
    potential_challenges = fields.Html(string='Potential Challenges')
    preparation = fields.Html(string='Preparation')
    action_plans = fields.Html(string='Action Plans')
    survey_count = fields.Integer(compute='_compute_survey_count', string="Survey Count")
    survey_ids = fields.One2many('ideatime.task.survey', 'task_survey_id', string='Survey')
    jo_accept_count = fields.Integer(compute="_compute_jo_count", string="JO Count")
    jo_accept_ids = fields.One2many('jo.acceptance', 'task_id', string='Jo Accept')
    design_proposal_count = fields.Integer(compute="_compute_design_count", string="Design Proposal")
    design_proposal_ids = fields.One2many('design.proposal', 'task_id', string='Design Proposal')
    responsible_person = fields.Html()
    department = fields.Html(string="Department Which department?")
    task_department_id = fields.Many2many('hr.department')
    resposnsible_team = fields.Html(string="Responsible Team")
    deadline = fields.Html()
    action_steps = fields.Html()
    partner = fields.Html()

    @api.depends('design_proposal_ids')
    def _compute_design_count(self):
        for task in self:
            task.design_proposal_count = len(task.design_proposal_ids)

    @api.depends('jo_accept_ids')
    def _compute_jo_count(self):
        for task in self:
            task.jo_accept_count = len(task.jo_accept_ids)

    @api.depends('survey_ids')
    def _compute_survey_count(self):
        for task in self:
            task.survey_count = len(task.survey_ids)

    def action_task_surveyinfo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'ideatime_project.project_subtask_survey',
            'model': 'project.task',
            'report_type': "qweb-html",
            'name': "Decoration process survey form",
        }

    @api.depends('meeting_ids')
    def _compute_meeting_count(self):
        for task in self:
            task.meeting_count = len(task.meeting_ids)

    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }
