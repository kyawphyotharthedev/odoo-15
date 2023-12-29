from odoo import fields, models


class ActionstepTaskLine(models.Model):
    _name = 'actionstep.task.line'
    _description = 'Action Step Task Line'

    name = fields.Char()


class ActionstepTemplate(models.Model):
    _name = 'actionstep.template'
    _description = 'Action Step Template'

    name = fields.Char(string='Name', required=True)
    actionstep_line_id = fields.One2many('actionstep.template.line', 'actionstep_id')


class ActionstepTemplateLine(models.Model):
    _name = 'actionstep.template.line'
    _description = 'Action Step Template Line'

    name = fields.Char(string='Action Step', required=True)
    actionstep_id = fields.Many2one('actionstep.template')
    actionstep_task_id = fields.Many2many('actionstep.task.line', string='Task')
