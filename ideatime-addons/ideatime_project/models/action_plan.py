from odoo import fields, models, _


class ActionPlan(models.Model):
    _name = 'action.plan'
    _description = 'Action Plan'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Action Step', required=True)
    progress = fields.Float(compute="action_progress", string='Progress', recompute=True, default=0.0)
    actionstep_task = fields.Many2many('actionstep.task.line')

    def action_progress(self):
        task_obj = self.env['project.task']
        for record in self:
            total_task = 0
            total_done = 0
            get_task = task_obj.search([('action_step_id', '=', record.id)])
            for task in get_task:
                if not task.parent_id and task.stage_id.stage_state != 'cancel':
                    total_task += 1
                    if task.stage_id.stage_state == 'done':
                        total_done += 1

            if total_task != 0:
                record.progress = (total_done * 100) / total_task

    def open_action_task(self):
        kanban_view_id = self.env.ref('ideatime_project.ideatime_view_task_tree2').id
        form_view_id = self.env.ref('ideatime_project.project_task_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'views': [(kanban_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'kanban,form',
            'name': _('Tasks'),
            'res_model': 'project.task',
            'domain': "[('action_step_id', '=',active_id),('parent_id','=',False)]",
            'context': {'default_project_id': self.project_id.id, 'default_action_step_id': self.id}
        }
