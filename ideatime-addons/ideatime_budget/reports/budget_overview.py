# -*- coding: utf-8 -*-

import json

from odoo import api, models, fields, _
from odoo.tools import float_round

cost_type_key_desc = {
    'self': 'Self Purchase',
    'proc': 'Procurement Purchase',
    'deli': 'Stock Delivery',
}


class ReportBudgetOverview(models.AbstractModel):
    _name = 'budget.overview.report'
    _description = 'Budget Overview Report'

    @api.model
    def _get_procurement_reference(self, batch, product_id=None, project_id=None, budget_id=None, batch_id=None,
                                   usage_type=None):
        res = {}
        purchase_order = self.env['purchase.order'].search([
            ('project_id', '=', project_id),
            ('budget_id', '=', budget_id),
            ('batch_id', '=', batch_id),
            ('state', '=', 'purchase'),
        ], order='id')

        for order in purchase_order:
            for line in order.order_line:
                if line.product_id.id == product_id:
                    key = str(order.id) + str(line.id) + str(product_id)
                    res[key] = {
                        'quantity': line.product_qty,
                        'unit_price': line.price_unit,
                        'price_subtotal': line.price_subtotal,
                        'reference': order.name,
                        'usage_type': usage_type,
                    }

        return res

    @api.model
    def _get_self_reference(self, batch, product_id=None, project_id=None, budget_id=None, batch_id=None,
                            usage_type=None):
        res = {}
        hr_expense = self.env['hr.expense'].search([
            ('project_id', '=', project_id),
            ('budget_id', '=', budget_id),
            ('batch_id', '=', batch_id),
            ('state', 'in', ['approved', 'done']),
        ], order='id')

        for exp in hr_expense:
            if exp.product_id.id == product_id:
                res[exp.name] = {
                    'quantity': exp.quantity,
                    'unit_price': exp.unit_amount,
                    'price_subtotal': exp.total_amount,
                    'reference': exp.product_id.name,
                    'usage_type': usage_type,
                }

        return res

    @api.model
    def _get_actual_reference(self, batch, usage_type, project_id=None, budget_id=None):
        actual_ref = {}
        if (usage_type == 'proc'):
            actual_ref = self._get_procurement_reference(batch, batch.product_id.id, project_id,
                                                         budget_id, batch.batch_id.id, usage_type)
        elif (usage_type == 'self'):
            actual_ref = self._get_self_reference(batch, batch.product_id.id, project_id,
                                                  budget_id, batch.batch_id.id, usage_type)
        return actual_ref



    @api.model
    def _convert_obj(self, rec_id, parent_id, level, product_id, product_name, qty, uom, price, amount, actual_cost,
                     diff_amount,
                     usage_type, show_hide='hidden'):
        return {
            'id': rec_id,
            'parent_id': parent_id,
            'level': level,
            'product_id': product_id,
            'product_name': product_name,
            'product_uom_qty': qty,
            'product_uom': uom,
            'unit_price': price,
            'total': amount,
            'actual_cost': actual_cost,
            'diff_amount': diff_amount,
            'usage_type': usage_type,
            'show_hide': show_hide,
            'child': None,

        }

    @api.model
    def get_html(self, budget_approval_id=False):
        res = self._get_report_data(budget_approval_id=budget_approval_id)
        res['lines']['report_type'] = 'html'
        res['lines'] = self.env.ref('ideatime_budget.report_budget_overview')._render({'data': res['lines']})
        return res

    @api.model
    def _get_report_data(self, budget_approval_id):
        lines = {}
        lines = self._get_budget_line(budget_approval_id, level=1)
        return {
            'lines': lines,
        }

    def _get_budget_line(self, budget_approval_id=False, line_id=False, level=False):

        budget_approval = self.env['budget.approval'].browse(budget_approval_id)
        estimate_line = self._get_budget_data_line(budget_approval, 0)
        account_payment = self._get_account_payment(budget_approval)
        lines = {
            'budget': budget_approval,
            'level': level or 0,
            'estimate_line': estimate_line,
            'account_payment': account_payment,
        }
        return lines

    def _convert_budget_line_to_object(self, rec_id, parent_id, line, level):
        return self._convert_obj(rec_id, parent_id, level, line.product_id.id, line.product_id.name,
                                 line.product_uom_qty,
                                 line.product_uom.name, line.price_unit, line.cost_estimate, '', '', '', 'shown')

    def _convert_cost_to_object(self, rec_id, parent_id, line, level):
        return self._convert_obj(rec_id, parent_id, level + 1, line.product_id.id,
                                 line.product_id.name, line.product_uom_qty,
                                 line.product_uom.name, line.unit_price,
                                 line.total_amount, '', '',
                                 cost_type_key_desc.get(line.usage_type)
                                 )

    def _convert_part_a_line_to_object(self, rec_id, parent_id, obj, line, level):

        return self._convert_obj(rec_id, parent_id, level + 1,
                                 line.product_id.id,
                                 line.batch_id.name, line.product_uom_qty,
                                 line.unit.name, line.unit_price,
                                 line.total_amount, '', '', '')

    def _convert_po_to_object(self, rec_id, parent_id, line, level):
        return self._convert_obj(rec_id, parent_id, level + 2, '', line.get('reference'),
                                 line.get('quantity'), '', line.get('unit_price'),
                                 '', line.get('price_subtotal'), '', '')

    def _prepare_payment(self, payment):
        return {
            'name': payment.name,
            'date': payment.date,
            'source': payment.journal_id.name,
            'destination': payment.destination_journal_id.name,
            'bank_reference': payment.bank_reference,
            'cheque_reference': payment.cheque_reference,
            'memo': payment.ref,
            'amount': payment.amount
        }

    def _get_account_payment(self, obj):
        account_payment = self.env['account.payment'].search(
            [('budget_approval_id', '=', obj.id), ('state', '=', 'posted'), ('payment_type', '=', 'outbound')])
        payment = []
        for pay in account_payment:
            payment.append(self._prepare_payment(pay))

        return payment

    def _get_budget_detail_line(self, obj, level, res):
        rec_id = 0
        parent_id = 0
        budget_key = str(obj.id)
        for parta in obj.approval_budget_line_id:
            parta_key = budget_key + parta._name + str(parta.id)
            rec_id += 1
            res[parta_key] = self._convert_budget_line_to_object(rec_id, parent_id, parta, level)
            res[parta_key]['child'] = parta.order_line_parta_cost_ids.ids
            parta_line_total = 0
            parent_id = rec_id
            direct_parent_id = rec_id
            for direct in parta.order_line_parta_cost_ids:
                direct_material_key = parta_key + direct._name + str(direct.id)
                rec_id += 1
                res[direct_material_key] = self._convert_cost_to_object(rec_id, direct_parent_id, direct, level)
                direct_parent_id = rec_id
                rec_id = self._append_cost_line_to_object(direct_material_key, rec_id, direct_parent_id, direct,
                                                          level + 1, obj.id,
                                                          obj.project_id.id, res)

                direct_parent_id = direct_parent_id - 1
                parta_line_total += 0 if res[direct_material_key]['actual_cost'] == '' else res[direct_material_key][
                    'actual_cost']

            res[parta_key]['actual_cost'] = parta_line_total
            res[parta_key]['diff_amount'] = float(
                0 if res[parta_key]['total'] == '' else res[parta_key]['total']) - parta_line_total

        for partb in obj.project_cost_estimate_part_id:
            partb_key = budget_key + partb._name + str(partb.id)
            rec_id += 1
            res[partb_key] = self._convert_budget_line_to_object(rec_id, parent_id, partb, level)
            # res[partb_key]['child'] = partb.budget_batch_line_id

            parent_id = rec_id
            rec_id = self._append_cost_line_to_object(partb_key, rec_id, parent_id, partb, level,
                                                      obj.id,
                                                      obj.project_id.id, res)

        for partc in obj.project_cost_estimate_partc_id:
            partc_key = budget_key + partc._name + str(partc.id)
            rec_id += 1
            res[partc_key] = self._convert_budget_line_to_object(rec_id, parent_id, partc, level)
            # res[partb_key]['child'] = partb.budget_batch_line_id

            parent_id = rec_id
            rec_id = self._append_cost_line_to_object(partc_key, rec_id, parent_id, partc, level,
                                                      obj.id,
                                                      obj.project_id.id, res)

        return res.values()

    def _append_cost_line_to_object(self, reference_key, rec_id, parent_id, obj, level, budget_id, project_id, res):
        direct_material_cost_total = 0
        res[reference_key]['child'] = obj.budget_batch_line_id
        for batch in obj.budget_batch_line_id:
            batch_key = reference_key + batch._name + str(batch.id)
            batch_total = 0
            rec_id += 1
            res[batch_key] = self._convert_part_a_line_to_object(rec_id, parent_id, obj, batch, level)

            actual_ref = self._get_actual_reference(batch, obj.usage_type, project_id, budget_id)
            if len(actual_ref) > 0:
                res[batch_key]['child'] = actual_ref
                parent_id = rec_id

                batch_total, rec_id = self.append_reference_detail_to_object(batch_key, actual_ref, batch_total, level,
                                                                             parent_id,
                                                                             rec_id, res)
                parent_id = parent_id - 1
            res[batch_key]['actual_cost'] = batch_total if batch_total != 0 else ''
            res[batch_key]['usage_type'] = cost_type_key_desc.get(obj.usage_type)
            res[batch_key]['diff_amount'] = float(res[batch_key]['total']) - batch_total
            direct_material_cost_total += batch_total

        res[reference_key]['actual_cost'] = direct_material_cost_total
        res[reference_key]['diff_amount'] = float(res[reference_key]['total']) - direct_material_cost_total
        return rec_id

    def append_reference_detail_to_object(self, reference_key, actual_ref, batch_total, level, parent_id, rec_id, res):
        for po in actual_ref:
            reference_key = reference_key + actual_ref[po].get('reference')
            batch_total += actual_ref[po].get('price_subtotal')
            rec_id += 1
            res[reference_key] = self._convert_po_to_object(rec_id, parent_id, actual_ref[po], level)
            key = actual_ref[po].get('usage_type')
            res[reference_key]['usage_type'] = cost_type_key_desc.get(
                actual_ref[po].get('usage_type'))
        return batch_total, rec_id

    def _get_budget_data_line(self, budget_approval, level):
        res = self._get_budget_detail_line(budget_approval, level, {})
        line = []
        for data in res:
            line.append(data)
        return line
