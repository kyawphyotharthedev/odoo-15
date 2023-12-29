
import re
from odoo import api, fields, Command, models, _



class HrExpense(models.Model):
    _inherit = "hr.expense"

    product_id = fields.Many2one('product.product', string='Product', readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                         'approved': [('readonly', False)], 'refused': [('readonly', False)]},
                                 domain="[('is_service_item', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 ondelete='restrict')

    project_id = fields.Many2one('project.project', string='Project', required="True")
    budget_id = fields.Many2one('budget.approval', required="True")
    batch_id = fields.Many2one('approval.budget.line', domain="[('approval_budget_id', '=',budget_id)]",
                               required="True")


    def _prepare_move_values(self):
        self.ensure_one()
        res = super(HrExpense, self)._prepare_move_values()
        res['project_id'] = self.project_id
        return res

class BudgetApproval(models.Model):
    _inherit = 'budget.approval'

    expense_ids = fields.One2many('hr.expense', 'budget_id', string="Expenses")