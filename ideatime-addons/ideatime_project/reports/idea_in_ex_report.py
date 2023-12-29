# -*- coding: utf-8 -*-

from odoo import api, models


class ReportIdeaInEx(models.AbstractModel):
    _name = 'report.ideatime_project.report_in_ex'
    _description = 'Income Expense Report'

    @api.model
    def get_html(self, proj_id=False):
        res = self._get_report_data(proj_id=proj_id)
        res['data']['report_type'] = 'html'
        res['data']['report_structure'] = 'all'
        res['data'] = self.env.ref('ideatime_project.report_idea_in_exp')._render({'data': res['data']})
        return res

    @api.model
    def _get_report_data(self, proj_id):

        project_obj = self.env['project.project'].browse(proj_id)
        exp_voucher = self.env['expense.voucher'].search([('project_ids', 'in', (proj_id))])
        inv_list = []
        exp_list = []
        for sale_order in project_obj.sale_ids:
            for invoice in sale_order.invoice_ids:
                if invoice.move_type == 'out_invoice' and invoice.state == 'open':
                    inv_list.append({
                        'invoice': invoice
                    })

        for expense in exp_voucher:
            exp_list.append({
                'expense': expense,
                'amount_total': expense.amount_total / len(expense.project_ids)
            })
        return {
            'data': {'name': project_obj.name,
                     'currency': self.env.user.company_id.currency_id,
                     'inv_list': inv_list,
                     'exp_list': exp_list,
                     'profit': project_obj.profit
                     },

        }

    @api.model
    def get_inv_line(self, inv_id, level=0):
        inv_obj = self.env['account.move'].browse(inv_id)
        lines = []
        for inv_line in inv_obj.invoice_line_ids:
            if not inv_line.display_type:
                lines.append({
                    'product_name': inv_line.product_id.name,
                    'qty': inv_line.quantity,
                    'price': inv_line.price_unit,
                    'uom': inv_line.uom_id.name,
                    'subtotal': inv_line.price_subtotal
                })
        values = {
            'inv_id': inv_id,
            'currency': self.env.user.company_id.currency_id,
            'incomes': lines,
            'level': level,
        }
        return self.env.ref('ideatime_project.report_inv_line')._render({'data': values})

    @api.model
    def get_exp_line(self, exp_id, level=0):
        exp_obj = self.env['expense.voucher'].browse(exp_id)
        lines = []
        for exp_line in exp_obj.voucher_line_ids:
            lines.append({
                'product_name': exp_line.product_id.name,
                'qty': exp_line.qty,
                'price': exp_line.price_unit,
                'uom': exp_line.uom_id.name,
                'total_proj': len(exp_obj.project_ids),
                'subtotal': (exp_line.price_subtotal) / len(exp_obj.project_ids)
            })
        values = {
            'exp_id': exp_id,
            'currency': self.env.user.company_id.currency_id,
            'incomes': lines,
            'level': level,
        }
        return self.env.ref('ideatime_project.report_exp_line')._render({'data': values})
