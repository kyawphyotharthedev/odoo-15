from odoo import fields, models


class IdeaIncomeExpense(models.Model):
    _name = 'idea.income.expense'
    _description = 'Income & Expense'

    def compute_in_ex(self):
        in_ex_line_obj = self.env['idea.income.expense.line']
        for sale_order in self.project_id.sale_ids:
            for invoice in sale_order.invoice_ids:
                if invoice.type == 'out_invoice' and invoice.state == 'open':
                    for inv_line in invoice.invoice_line_ids:
                        in_ex_line_obj |= in_ex_line_obj.new({'product_id': inv_line.product_id.id,
                                                              'income': inv_line.price_subtotal, })

        return in_ex_line_obj

    name = fields.Char(string='Name', required=True, readonly=True)
    project_id = fields.Many2one('project.project')
    in_ex_line_ids = fields.One2many('idea.income.expense.line', 'in_ex_id', compute='compute_in_ex', store=True)


class IdeaIncomeExpenseLine(models.Model):
    _name = 'idea.income.expense.line'
    _description = 'Income & Expense Line'

    in_ex_id = fields.Many2one('idea.income.expense')
    product_id = fields.Many2one('product.product')
    income = fields.Float(string='Income')
    expense = fields.Float(string='Expense')
