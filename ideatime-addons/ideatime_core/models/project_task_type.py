from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    project_type_ids = fields.Many2many('project.type', string='Project Type', domain="[('right_ids','=',False)]")
    stage_type = fields.Selection([
        ('project', 'Project'),
        ('task', 'Task'),
    ],
        string='Stage Type', required=True,
        default='task')
    stage_state = fields.Selection([
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ],
        string='Stage State',
        default='')
