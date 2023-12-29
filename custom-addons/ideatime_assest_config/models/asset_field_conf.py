# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
#
# class AssetProject(models.Model):
#     _inherit = "account.asset.asset"
#
#     project_id = fields.Many2one('project.project', string="Project", required=True)
#
#     @api.model
#     def _domain_project_id(self):
#         journal_entries = self.env['account.move'].search([('type', '=', 'entry')])
#         project_ids = journal_entries.mapped('project_id.id')
#         return [('id', 'in', project_ids)]
#
#     @api.depends('account_move_ids')
#     def _compute_project_id(self):
#         for asset in self:
#             journal_entries = asset.account_move_ids.filtered(lambda move: move.type == 'entry')
#             for journal_entry in journal_entries:
#                 if journal_entry.project_id:
#                     asset.project_id = journal_entry.project_id
#                     break
    #
    # @api.constrains('account_move_ids')
    # def _check_project_id(self):
    #     for asset in self:
    #         if not asset.project_id:
    #             raise ValidationError("The project field is required for all assets.")

