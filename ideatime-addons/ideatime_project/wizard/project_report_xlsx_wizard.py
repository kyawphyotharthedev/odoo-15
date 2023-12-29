from odoo import models, fields


class ProjectWizard(models.TransientModel):
    _name = "project.report.wizard"
    _description = "Project Report Wizard"

    proj_type_id = fields.Many2many('project.type', domain="[('left_id','=',id)]")

    def print_report(self):
        self.ensure_one()
        data = {'form': self.read(['proj_type_id'])[0]}
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'ideatime_project.project_report_xlsx'), ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=data)
