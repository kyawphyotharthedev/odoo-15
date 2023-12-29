from odoo import models


class ProjectAnalysisXlsReport(models.AbstractModel):
    _name = 'report.ideatime_sale.project_analysis_report_id'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Project Analysis Report"

    def get_display_data(self, objects):
        summary_line = []
        for line in objects.order_expense_line:
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

        for line in objects.order_line:

            all_dir_order_line = self.env['direct.material.cost'].search([('so_line_id', 'in', line.ids)])

            for line in all_dir_order_line:

                if line.so_line_id:
                    for dir_line in line.so_line_id:
                        total_amount += line.qty * line.unit_price

                        dir.update({'dir_cost': total_amount})
                        dir_cost.append(dir)

        return dir_cost

    def get_indir_order_line_display_data(self, objects):
        indir_cost = []
        indir = {}
        indrtotal_amount = 0

        for line in objects.order_line:

            all_dir_order_line = self.env['in.direct.material.cost'].search([('so_line_id', 'in', line.ids)])
            for line in all_dir_order_line:
                if line.so_line_id:
                    for indir_line in line.so_line_id:
                        indrtotal_amount += line.qty * line.unit_price

                        indir.update({'indr_cost': indrtotal_amount})
                        indir_cost.append(indir)

        return indir_cost

    def get_dir_labour_order_line_display_data(self, objects):
        dir_labour_cost = []
        dir_labour_cost_list = {}
        dirlabour_amount = 0
        for line in objects.order_line:

            all_dir_order_line = self.env['direct.labour.cost'].search([('so_line_id', 'in', line.ids)])
            for line in all_dir_order_line:
                if line.so_line_id:
                    for dirlabour_line in line.so_line_id:
                        dirlabour_amount += line.qty * line.unit_price

                        dir_labour_cost_list.update({'dirlabour_cost': dirlabour_amount})
                        dir_labour_cost.append(dir_labour_cost_list)

        return dir_labour_cost

    def get_thirdparty_order_line_display_data(self, objects):
        thirdparty_cost = []
        thirdpartycost_list = {}
        thirdparty_amount = 0
        for line in objects.order_line:

            all_dir_order_line = self.env['thirdparty.cost.contractor'].search([('so_line_id', 'in', line.ids)])
            for line in all_dir_order_line:
                if line.so_line_id:
                    for thirdparty_con_line in line.so_line_id:
                        thirdparty_amount += line.qty * line.unit_price

                        thirdpartycost_list.update({'thirdparty_cost': thirdparty_amount})
                        thirdparty_cost.append(thirdpartycost_list)

        return thirdparty_cost

    def get_subthirdparty_order_line_display_data(self, objects):
        subthirdparty_cost = []
        for line in objects.order_line:

            subthirdpartycost_list = {}
            subthirdparty_amount = 0

            all_dir_order_line = self.env['thirdparty.cost.subcontractor'].search([('so_line_id', 'in', line.ids)])
            for line in all_dir_order_line:

                if line.so_line_id:
                    for subthirdpary_line in line.so_line_id:
                        subthirdparty_amount += line.qty * line.unit_price

                        subthirdpartycost_list.update({'subthirdparty_cost': subthirdparty_amount})
                        subthirdparty_cost.append(subthirdpartycost_list)

        return subthirdparty_cost

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

        display_row = 1

        sheet.write(display_row, 0, 'Document name', format5)
        sheet.write(display_row, 1, 'Project estimate budget form', format8)
        display_row += 1
        sheet.write(display_row, 0, 'Project code', format5)
        sheet.write(display_row, 1, objects.project_id.name or '', format8)
        display_row += 1
        sheet.write(display_row, 0, 'Project name', format5)
        sheet.write(display_row, 1, objects.project_name, format8)
        display_row += 1

        sheet.merge_range(display_row, 0, display_row, 3, 'General Information', format9)
        display_row += 1
        sheet.merge_range(display_row, 0, display_row, 1, 'Party A', format2)
        sheet.merge_range(display_row, 2, display_row, 3, 'Party B', format2)
        display_row += 1
        sheet.write(display_row, 0, 'Client name', format6)
        sheet.write(display_row, 1, objects.partner_id.name, format7)
        sheet.merge_range(display_row, 2, display_row, 3, 'Idea Time Advertisting Company', format1)
        display_row += 1
        sheet.write(display_row, 0, 'Address of corporate', format6)
        sheet.write(display_row, 1, objects.partner_id.street or '', format7)
        sheet.write(display_row, 2, 'Address of corporate', format6)
        sheet.write(display_row, 3, objects.company_id.street or '', format7)
        display_row += 1
        sheet.write(display_row, 0, 'PIC name', format6)
        sheet.write(display_row, 1, '', format7)
        sheet.write(display_row, 2, 'PIC name', format6)
        sheet.write(display_row, 3, objects.project_id.user_id.name or '', format7)
        display_row += 1
        sheet.write(display_row, 0, 'Phone no', format6)
        sheet.write(display_row, 1, objects.partner_id.phone or '', format7)
        sheet.write(display_row, 2, 'Phone no', format6)
        sheet.write(display_row, 3, objects.company_id.phone or '', format7)
        display_row += 1
        sheet.write(display_row, 0, 'Service group', format6)
        sheet.merge_range(display_row, 1, display_row, 3, objects.project_id.cate_group_id.name or '', format7)
        display_row += 1
        sheet.write(display_row, 0, 'Service sector', format6)
        sheet.merge_range(display_row, 1, display_row, 3, objects.project_id.cate_sector_id.name or '', format7)
        display_row += 1
        sheet.write(display_row, 0, 'Project site', format6)
        sheet.merge_range(display_row, 1, display_row, 3, objects.project_id.project_site or '', format7)
        display_row += 1
        sheet.merge_range(display_row, 0, display_row, 4, 'Project estimate budget analysis chart', format9)
        display_row += 1

        sheet.write(display_row, 0, '', format1)
        sheet.write(display_row, 1, 'Cost', format1)
        sheet.write(display_row, 2, '(%)', format1)

        orderline_display_data = self.get_order_line_display_data(objects)
        display_row += 1

        sheet.write(display_row, 0, 'Direct Materials Cost', format1)
        for order_line_data in orderline_display_data:
            sheet.write(display_row, 1, order_line_data['dir_cost'], format1)
            sheet.write(display_row, 2, '=B16/B36%', format1)

        indr_display_data = self.get_indir_order_line_display_data(objects)
        display_row += 1
        sheet.write(display_row, 0, 'Indirect Materials Cost', format1)
        for order_line_data in indr_display_data:
            sheet.write(display_row, 1, order_line_data['indr_cost'], format1)
            sheet.write(display_row, 2, '=B17/B36%', format1)

        dr_labour_display_data = self.get_dir_labour_order_line_display_data(objects)
        display_row += 1

        sheet.write(display_row, 0, 'Direct Labour Cost', format1)
        for dirlaborder_line_data in dr_labour_display_data:
            sheet.write(display_row, 1, dirlaborder_line_data['dirlabour_cost'], format1)
            sheet.write(display_row, 2, '=B18/B36%', format1)

        thirdparty_display_data = self.get_thirdparty_order_line_display_data(objects)
        display_row += 1

        sheet.write(display_row, 0, 'Thirdparty Cost Contractor', format1)
        for thirdparty_line_data in thirdparty_display_data:
            # sheet.write(display_row, 1,str(thirdparty_line_data['thirdparty_percentage']) + '%',format1)

            sheet.write(display_row, 1, thirdparty_line_data['thirdparty_cost'], format1)
            sheet.write(display_row, 2, '=B19/B36%', format1)

        subthirdparty_display_data = self.get_subthirdparty_order_line_display_data(objects)
        display_row += 1

        sheet.write(display_row, 0, 'Thirdparty Cost subcontractor', format1)
        for subthirdparty_line_data in subthirdparty_display_data:
            # sheet.write(display_row, 1,str(subthirdparty_line_data['subthirdparty_percentage']) + '%',format1)

            sheet.write(display_row, 1, subthirdparty_line_data['subthirdparty_cost'], format1)
            sheet.write(display_row, 2, '=B20/B36%', format1)

        display_row += 1

        display_data = self.get_display_data(objects)

        for data in display_data:
            sheet.write(display_row, 0, data['name'], format1)
            sheet.write(display_row, 1, data['cost'], format1)
            sheet.write(display_row, 2, '=' + str(data["cost"]) + '/B36%', format1)

            display_row += 1

        sheet.write('A36', 'Grand Total (MMK) :', format1)
        sheet.write('B36', '=SUM(B12:B35)', format1)
        sheet.write('C36', '=SUM(C12:C35)', format1)

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
        sheet.insert_chart('D16', draw_chart, {'x_scale': 0.53, 'y_scale': 1.5})
