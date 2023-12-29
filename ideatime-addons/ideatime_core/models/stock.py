from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one('project.project', string='Project', required=True)
    project_site_id = fields.Char(related="project_id.project_site")
    project_name = fields.Char(compute="_compute_project_name")
    project_client_id = fields.Char(related="project_id.partner_id.name")
    analytic_account_id = fields.Many2one('account.analytic.account')

    @api.onchange('project_id')
    def onchange_project_id(self):

        analytic_account_obj = self.env['account.analytic.account'].search([('name', '=', self.project_id.name)])
        self.analytic_account_id = False
        for analytic in analytic_account_obj:
            self.analytic_account_id = analytic.id

    @api.onchange('project_id')
    def _compute_project_name(self):
        for record in self:

            service_project_name = []
            if record.project_client_id:
                service_project_name.append(record.project_client_id)

            if record.project_id.cate_sector_id:
                service_project_name.append(str(record.project_id.cate_sector_id.name))
            if record.project_id.cate_line_id:
                service_project_name.append(str(record.project_id.cate_line_id.name))

            if record.project_id.manual_project_name:
                service_project_name.append(str(record.project_id.manual_project_name))

            record.project_name = " ".join(str(x) for x in service_project_name)


class StockMove(models.Model):
    _inherit = "stock.move"

    projectdir_line_id = fields.Many2one('projectdir.material.cost', 'Direct Material Cost Line', index=True)
    projectindir_line_id = fields.Many2one('projectindir.material.cost', 'In Direct Material Cost Line', index=True)


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    project_id = fields.Many2one('project.project', string='Project')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['project_id', 'direct_line_id', 'in_direct_line_id', 'projectdir_line_id', 'projectindir_line_id',
                   'partner_id']
        return fields
