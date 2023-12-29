from odoo import models


class ProjectAnalysisXlsReport(models.AbstractModel):
    _name = 'report.ideatime_budget.budget_analysis_report_id'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Project Cost Estimate Analysis"

    def get_display_data(self, objects):
        summary_line = []
        for line in objects.project_cost_estimate_part_id:
            if line.display_type:
                summary_line.append({
                    'name': line.name,
                    'cost': 0,
                })
            else:
                if summary_line:
                    summary_line[-1]['cost'] += line.price_subtotal
        return summary_line

    def get_order_line_display_data(self, objects):
        dir_cost = []
        dir = {}
        total_amount = 0

        for o_line in objects.approval_budget_line_id:
            all_dir_order_line = self.env['budget.parta.cost'].search(
                [('budget_order_line_id', 'in', o_line.ids)])
            for line in all_dir_order_line:
                if line.budget_order_line_id:
                    for dir_line in line.budget_order_line_id:
                        total_amount += line.qty * line.unit_price
                        dir.update({'dir_cost': total_amount})
                        dir_cost.append(dir)
        return dir_cost








    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'center',
             'valign': 'vcenter', 'bold': True})
        format1.set_align('vcenter')
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'center',
             'valign': 'vcenter', 'bold': False})
        format2.set_align('vcenter')
        format2.set_bg_color('#073054')
        format2.set_font_color('white')

        format3 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'right',
             'valign': 'right', 'bold': True})
        format3.set_align('vcenter')
        format4 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'right',
             'valign': 'right', 'bold': True})
        format5 = workbook.add_format(
            {'font_size': 12, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'right',
             'valign': 'right', 'bold': True})
        format6 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'right',
             'valign': 'right', 'bold': True})
        format7 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'left',
             'valign': 'left', 'bold': True})
        format8 = workbook.add_format(
            {'font_size': 12, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'left',
             'valign': 'left', 'bold': True})
        format9 = workbook.add_format(
            {'font_size': 10, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'center',
             'valign': 'vcenter', 'bold': True})
        format9.set_bg_color('#40180B')
        format9.set_font_color('white')
        format9.set_align('vcenter')
        sheet.insert_image('A0', 'ideatime_header.jpg')
        myformat = workbook.add_format()
        myformat.set_pattern(0)

        sheet.set_column(0, 0, 25)
        sheet.set_column(1, 1, 40)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 50)

        display_row = 1

        sheet.write(display_row, 0, 'Document name', format5)
        sheet.merge_range(display_row, 1, display_row, 3, 'Project estimate budget form', format8)
        display_row += 1
        sheet.write(display_row, 0, 'Project code', format5)
        sheet.merge_range(display_row, 1, display_row, 3, objects.name or '', format8)
        display_row += 1
        sheet.write(display_row, 0, 'Project name', format5)
        sheet.merge_range(display_row, 1, display_row, 3, '', format8)
        display_row += 1
        display_row += 1
        sheet.merge_range(display_row, 0, display_row, 3, 'Project estimate budget analysis chart', format9)

        display_row += 1
        sheet.write(display_row, 0, '', format1)
        sheet.write(display_row, 1, 'Cost', format1)
        sheet.write(display_row, 2, '(%)', format1)

        orderline_display_data = self.get_order_line_display_data(objects)
        display_row += 1
        sheet.write(display_row, 0, 'Direct Materials Cost', format6)
        for order_line_data in orderline_display_data:
            sheet.write(display_row, 1, order_line_data['dir_cost'], format1)
            sheet.write(display_row, 2, '=B8/B28%', format1)






       

        display_row += 1
        display_data = self.get_display_data(objects)
        for data in display_data:
            sheet.write(display_row, 0, data['name'], format1)
            sheet.write(display_row, 1, data['cost'], format1)
            sheet.write(display_row, 2, '=' + str(data["cost"]) + '/B28%', format1)
            display_row += 1

        sheet.write('A28', 'Grand Total (MMK) :', format1)
        sheet.write('B28', '=SUM(B8:B27)', format1)
        sheet.write('C28', '=SUM(C8:C27)', format1)

        draw_chart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})
        draw_chart.add_series({
            'categories': '=Sheet1!$A$16:$A$35',
            'fill': {'color': '#0e95e3'},
            'values': '=Sheet1!$C$16:$C$35',
            'line': {'color': '#0e95e3'},
        })
        draw_chart.set_title({'name': 'Analysis chart'})
        draw_chart.set_x_axis({'line': {'none': True},
                               'visible': False
                               })
        draw_chart.set_y_axis({'reverse': True,
                               'line': {'none': True},
                               })
        draw_chart.set_legend({'none': True})
        sheet.insert_chart('D7', draw_chart, {'x_scale': 0.7, 'y_scale': 1.5})
