from odoo import models


class ProjectReportXlsx(models.AbstractModel):
    _name = 'report.ideatime_project.project_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Project Report XLSX'

    def get_project_type(self, data):
        proj_type_id = data['form'].get('proj_type_id')
        return proj_type_id

    def generate_xlsx_report(self, workbook, data, objects):

        header_format = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        data_format = workbook.add_format({'align': 'center', 'valign': 'top'})

        sheet = workbook.add_worksheet("Sale Item Report")
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 14, 25)

        project_type_range = self.get_project_type(data)
        # query_string = []
        # query_string =[('is_sale_item','=',data['form'].get('is_sale_item'))]
        # if project_type_range:
        #     query_string.append(('proj_type_id','in',project_type_range))

        get_project_type = self.env['project.type'].search([('left_id', 'in', project_type_range)])
        get_project = self.env['project.project'].search([('proj_type_id', 'in', project_type_range)])
        heading_row = 0

        sheet.write(heading_row, 0, 'No', header_format)
        sheet.write(heading_row, 1, ' Business Type', header_format)
        sheet.write(heading_row, 2, 'Project Type', header_format)
        sheet.write(heading_row, 3, 'Project Code', header_format)
        sheet.write(heading_row, 4, 'Project Name', header_format)
        sheet.write(heading_row, 5, 'Client Name', header_format)
        sheet.write(heading_row, 6, 'Budget Total', header_format)
        sheet.write(heading_row, 7, 'Currency', header_format)
        sheet.write(heading_row, 8, 'Budget Total (MMK)', header_format)
        sheet.write(heading_row, 9, 'Budget Total (USD)', header_format)
        sheet.write(heading_row, 10, 'Budget Total (CNY)', header_format)
        sheet.write(heading_row, 11, 'Budget Total (THB)', header_format)
        sheet.write(heading_row, 12, 'Sale Order Total (MMK)', header_format)
        sheet.write(heading_row, 13, 'Sale Order Total (USD)', header_format)
        sheet.write(heading_row, 14, 'Process State', header_format)
        sheet.write(heading_row, 15, 'Project State', header_format)
        sheet.write(heading_row, 16, 'Project PIC', header_format)
        display_row = heading_row + 1
        no = 1
        if get_project_type:

            for data in get_project_type:

                sheet.write(display_row, 0, no, data_format)
                sheet.write(display_row, 1, data.left_id.name, data_format)
                sheet.write(display_row, 2, data.name, data_format)

                proj_row = display_row

                for proj in data.union_proj_type_project_ids:
                    sheet.write(proj_row, 3, proj.name, data_format)
                    sheet.write(proj_row, 4,
                                str(proj.partner_id.name) + ' ' + str(proj.cate_sector_id.name) + ' ' + str(
                                    proj.cate_line_id.name) + ' ' + str(proj.manual_project_name), data_format)
                    sheet.write(proj_row, 5, proj.partner_id.name, data_format)
                    budget_row = proj_row
                    budget_col = 6
                    if proj.budget_approval_ids:

                        mmk_budget_total = 0
                        usd_budget_total = 0
                        cny_budget_total = 0
                        baht_budget_total = 0
                        for budget_line in proj.budget_approval_ids:
                            sheet.write(budget_row, budget_col, budget_line.grand_total, data_format)
                            budget_col += 1
                            sheet.write(budget_row, budget_col, budget_line.currency_id.name, data_format)
                            budget_row += 1
                            budget_col = 6
                            if budget_line.currency_id.name == 'MMK':
                                mmk_budget_total += budget_line.grand_total
                                sheet.write(proj_row, 8, mmk_budget_total, data_format)
                            elif budget_line.currency_id.name == 'USD':
                                usd_budget_total += budget_line.grand_total
                                sheet.write(proj_row, 9, usd_budget_total, data_format)
                            elif budget_line.currency_id.name == 'CNY':
                                cny_budget_total += budget_line.grand_total
                                sheet.write(proj_row, 10, cny_budget_total, data_format)
                            elif budget_line.currency_id.name == 'THB':
                                baht_budget_total += budget_line.grand_total
                                sheet.write(proj_row, 11, baht_budget_total, data_format)

                    if proj.sale_ids:
                        mmk_sale_total = 0
                        usd_sale_total = 0
                        for sale_line in proj.sale_ids:
                            if sale_line.pricelist_id.currency_id.name == "MMK":

                                mmk_sale_total += sale_line.amount_total
                                sheet.write(proj_row, 12, mmk_sale_total, data_format)
                            elif sale_line.pricelist_id.currency_id.name == "USD":
                                usd_sale_total += sale_line.amount_total
                                sheet.write(proj_row, 13, usd_sale_total, data_format)
                    sheet.write(proj_row, 14, '', data_format)
                    sheet.write(proj_row, 15, proj.proj_type_stage_id.name, data_format)
                    sheet.write(proj_row, 16, proj.user_id.name, data_format)

                    proj_row = budget_row

                display_row = proj_row + 1
                no += 1
        else:
            sr = 1
            for proj_line in get_project:

                sheet.write(display_row, 0, sr, header_format)
                sheet.write(display_row, 1, proj_line.proj_type_id.name, header_format)
                sheet.write(display_row, 2, '', header_format)
                sheet.write(display_row, 3, proj_line.name, header_format)
                sheet.write(display_row, 4, 'Project Name', header_format)
                sheet.write(display_row, 5, proj_line.partner_id.name, header_format)
                if proj_line.budget_approval_ids:
                    mmk_budget_total = 0
                    usd_budget_total = 0
                    for budget_line in proj_line.budget_approval_ids:
                        if budget_line.currency_id.name == 'MMK':
                            mmk_budget_total += budget_line.grand_total
                            sheet.write(display_row, 6, mmk_budget_total, data_format)
                        elif budget_line.currency_id.name == 'USD':
                            usd_budget_total += budget_line.grand_total
                            sheet.write(display_row, 7, usd_budget_total, data_format)

                if proj_line.sale_ids:
                    mmk_sale_total = 0
                    usd_sale_total = 0
                    for sale_line in proj_line.sale_ids:
                        if sale_line.pricelist_id.currency_id.name == "MMK":

                            mmk_sale_total += sale_line.amount_total
                            sheet.write(display_row, 8, mmk_sale_total, data_format)
                        elif sale_line.pricelist_id.currency_id.name == "USD":
                            usd_sale_total += sale_line.amount_total
                            sheet.write(display_row, 9, usd_sale_total, data_format)
                sheet.write(display_row, 10, '', header_format)
                sheet.write(display_row, 11, proj_line.proj_type_stage_id.name, header_format)
                sheet.write(display_row, 12, proj_line.user_id.name, header_format)
                display_row += 1
                sr += 1


