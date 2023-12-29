from odoo import models, fields


class TaskChecklist(models.Model):
    _inherit = 'task.checklist'

    department_id = fields.Many2one('hr.department', string='Department')
