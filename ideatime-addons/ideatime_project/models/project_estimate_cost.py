from odoo import models, fields


class ProjectEstimateCost(models.Model):
    _name = 'project.estimate.cost'
    _description = 'Project Estimate Cost'

    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade', index=True,
                                 copy=False)
    cost_option_id = fields.Many2one('cost.option', string='Cost Option')
    name = fields.Text(string='Description')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    estimate_cost = fields.Float('Estimate Cost', required=True, default=0.0)
