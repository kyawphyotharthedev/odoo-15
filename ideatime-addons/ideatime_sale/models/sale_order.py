# -*- coding: utf-8 -*-

import base64
from itertools import groupby

from PIL import Image, ImageDraw, ImageFont

from odoo import fields, api, models, _
from odoo.tools.misc import get_lang

try:
    import myanmar

    try:
        from myanmar.converter import convert
    except ImportError:
        convert = None
except ImportError:
    myanmar = convert = None


class SaleOrder(models.Model):
    _inherit = "sale.order"

    project_budget_applicable_plan_lines = fields.One2many('project.budget.applicable.plan',
                                                           'project_budget_applicable_plan_id', string="PBAP lines")

    service_group_id = fields.Many2one('service.category.group')
    survey_id = fields.Many2one('ideatime.survey')
    sale_order_img = fields.Binary(string="Photo")
    order_expense_line = fields.One2many('expense.order.line', 'order_id', string='Expense Lines', copy=True,
                                         auto_join=True)
    agreement_period_id = fields.Many2one('agreement.period.template', string="Agreement Period Template")
    agreement_period_note = fields.Text()
    agreement_period_image = fields.Binary(string="Agreement Period Image", readonly=False)
    commencement_date = fields.Date()
    commencement_start_date = fields.Date()
    commencement_end_date = fields.Date()
    currency_template_id = fields.Many2one('currency.template')
    currency_note = fields.Text()
    currency_note_image = fields.Binary()
    price_fee_id = fields.Many2one('price.fee.template')
    price_fee_note = fields.Text()
    price_fee_note_image = fields.Binary()
    taxation_template_id = fields.Many2one('taxation.template')
    taxation_note = fields.Text()
    taxation_note_image = fields.Binary()
    payment_template_id = fields.Many2one('payment.template')
    payment_note = fields.Text()
    payment_note_image = fields.Binary()
    acceptance_template_id = fields.Many2one('acceptance.template')
    acceptance_note = fields.Text()
    acceptance_note_image = fields.Binary(string="Acceptance Note Image", readonly=False)
    obligation_template_id = fields.Many2one('obligation.template')
    obligation_note = fields.Text()
    obligation_note_image = fields.Binary(string="Obligation Note Image")
    contract_template_id = fields.Many2one('contract.template')
    contract_note = fields.Text()
    contract_note_image = fields.Binary(string="Contract Note Image")
    termination_template_id = fields.Many2one('termination.template')
    termination_note = fields.Text()
    termination_note_image = fields.Binary()
    arbitration_template_id = fields.Many2one('arbitration.template')
    arbitration_note = fields.Text()
    arbitration_note_image = fields.Binary()
    additional_agreement = fields.Text()
    expense_total_amount = fields.Monetary(string='Total Amount', compute="_compute_expense_total_amount")
    date_printed = fields.Char(string='Printed Date', compute="compute_print_date")
    agreement_file = fields.Binary(string='Order Agreegment File')
    file_name = fields.Char(string="File Name")
    estimate_filename = fields.Char(string="Estimate File Name")
    analysis_filename = fields.Char(string="Analysis File Name")
    agreement_confirm = fields.Boolean(compute="_compute_agreement_confirm")
    material_cost_confirm = fields.Boolean()

    project_cost_estimate_confirm = fields.Boolean(default=False, compute="_compute_budget_confirm")
    project_budget_applicable_plan_confirm = fields.Boolean(default=False, compute="_compute_budget_confirm")
    start_date = fields.Date()
    end_date = fields.Date()
    no_of_day = fields.Char(compute="_compute_remaining_days", store=True)
    grand_total_amount = fields.Float(compute="_compute_project_budget_total_amount")

    project_cost_estimate_file = fields.Binary(string='Project Cost Estimate File')
    project_estimate_anlaysis_file = fields.Binary(string="Project Cost Estimate Analysis")
    estimate_file_confirm = fields.Boolean(compute="_compute_project_cost_estimate_confirm")
    project_implement_approve = fields.Boolean()

    bd_senior_approve = fields.Boolean(default="False")
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='draft')
    order_agree_user_id = fields.Many2one('res.users', string='Approve Order Agreement User', tracking=True)
    order_agree_date_time = fields.Datetime(string='Approve Order Agreement Date', tracking=True)
    budget_user_id = fields.Many2one('res.users', string='Approve Budget User', tracking=True)
    budget_date_time = fields.Datetime(string='Approve Order Budget Date', tracking=True)
    check_user_id = fields.Many2one('res.users', string='Check User', tracking=True)
    check_date_time = fields.Datetime(string='Check Date', tracking=True)

    approve_user_id = fields.Many2one('res.users', string='Approve Purchase User', tracking=True)
    approve_date_time = fields.Datetime(string='Approve Purchase Date', tracking=True)
    bd_senior_manger = fields.Many2one('res.users', store=True)

    project_senior_approve = fields.Boolean(default=False, compute="_compute_project_senior_approve")
    current_user = fields.Many2one('res.users', compute='_get_current_user')

    finance_approve = fields.Boolean(default=False, compute="_compute_finance_approve")
    invoice_validate = fields.Boolean(default=False, compute="_compute_invoice_validate")
    bd_date = fields.Date(string="Date")
    client_name = fields.Many2one('res.partner')
    store_format = fields.Char()
    business_type = fields.Char()
    bd_project_name = fields.Char(string="Project name")
    location = fields.Char(string="Project area")
    tax_id = fields.Char()
    employee_id = fields.Many2one('res.partner', domain=[('customer', '=', False), ('supplier', '=', False)])
    bd_title1 = fields.Text(string="Title1")
    bd_title2 = fields.Text(string="Title2")
    bd_title3 = fields.Text(string="Title3")
    bd_title4 = fields.Text(string="Title4")
    bd_title5 = fields.Text(string="Title5")
    bd_title6 = fields.Text(string="Title6")
    bd_title7 = fields.Text(string="Title7")
    bd_title8 = fields.Text(string="Title8")
    bd_title9 = fields.Text(string="Title9")
    bd_title10 = fields.Text(string="Title10")
    invoice_date = fields.Date(string="Date")
    invoice_number = fields.Many2one('account.move')
    po_number = fields.Char()
    po_attached_file = fields.Binary()
    project_number = fields.Char()
    invoice_payment_term = fields.Many2one('account.payment.term')
    vendor_name = fields.Char()
    bank_name = fields.Char()
    bank_account_no = fields.Char(string="Bank Account Number")
    swift_code = fields.Char()
    invoice_title1 = fields.Text(string="Title1")
    invoice_title2 = fields.Text(string="Title2")
    invoice_title3 = fields.Text(string="Title3")
    invoice_title4 = fields.Text(string="Title4")
    invoice_title5 = fields.Text(string="Title5")
    invoice_title6 = fields.Text(string="Title6")
    invoice_title7 = fields.Text(string="Title7")
    invoice_title8 = fields.Text(string="Title8")
    invoice_title9 = fields.Text(string="Title9")
    invoice_title10 = fields.Text(string="Title10")
    budget_pricelist_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id.id)
    particular = fields.Text(compute="compute_particular")

    def compute_particular(self):
        for record in self:
            summary_line = []
            record.particular = ''
            for line in record.order_line:
                if line.display_type:
                    summary_line.append(line.name)
                record.particular = "\n".join(str(x) for x in summary_line)

    @api.depends('invoice_ids')
    def _compute_invoice_validate(self):
        for record in self:
            if not record.invoice_ids:
                record.invoice_validate = False
            for inv in record.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    record.invoice_validate = True
                else:
                    record.invoice_validate = False

    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
        # i think this work too so you don't have to loop
        self.update({'current_user': self.env.user.id})

    def action_approve(self):
        self.write(
            {'w_state': 'approve', 'approve_user_id': self.env.user.id, 'approve_date_time': fields.Datetime.now()})
        return

    def action_detail_check(self):
        self.write({'w_state': 'check', 'check_user_id': self.env.user.id, 'check_date_time': fields.Datetime.now()})
        return

    def action_budget(self):
        self.write({'w_state': 'budget', 'budget_user_id': self.env.user.id, 'budget_date_time': fields.Datetime.now()})
        return

    def action_order_agreement(self):
        self.write({'w_state': 'order_agreement', 'order_agree_user_id': self.env.user.id,
                    'order_agree_date_time': fields.Datetime.now()})
        return

    @api.depends('project_cost_estimate_file', 'project_estimate_anlaysis_file')
    def _compute_project_cost_estimate_confirm(self):
        if self.project_cost_estimate_file and self.project_estimate_anlaysis_file:
            self.estimate_file_confirm = True
        else:
            self.estimate_file_confirm = False

    @api.depends('project_budget_applicable_plan_lines.amount')
    def _compute_project_budget_total_amount(self):
        for budget in self:
            grand_total = 0
            for project_budget_line in self.project_budget_applicable_plan_lines:
                if self.project_budget_applicable_plan_lines:
                    grand_total += project_budget_line.amount
            budget.update({
                'grand_total_amount': grand_total,
            })

    @api.depends('start_date', 'end_date')
    def _compute_remaining_days(self):
        for record in self:
            if record.start_date and record.end_date:
                record.no_of_day = str((record.end_date - record.start_date).days)

    @api.depends('agreement_file')
    def _compute_agreement_confirm(self):
        if self.agreement_file:
            self.agreement_confirm = True
        else:
            self.agreement_confirm = False

    @api.depends('project_cost_estimate_file', 'project_estimate_anlaysis_file')
    def _compute_budget_confirm(self):
        if self.project_cost_estimate_file and self.project_estimate_anlaysis_file:
            self.project_cost_estimate_confirm = True
            self.project_budget_applicable_plan_confirm = True
        else:
            self.project_cost_estimate_confirm = False
            self.project_budget_applicable_plan_confirm = False

    def compute_print_date(self):
        self.date_printed = fields.Datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    @api.depends('order_expense_line.price_subtotal')
    def _compute_expense_total_amount(self):
        for expense in self:
            expense_total = 0
            for total_expense_line in self.order_expense_line:
                if self.order_expense_line:
                    expense_total += total_expense_line.price_subtotal
            expense.update({
                'expense_total_amount': expense_total,
            })

    @api.onchange('agreement_period_id')
    def onchange_agreement_period_template_id(self):
        if not self.agreement_period_id:
            return
        self.agreement_period_note = self.agreement_period_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.agreement_period_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.agreement_period_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)
            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.agreement_period_image = image

    @api.onchange('currency_template_id')
    def onchange_currency_template_id(self):
        if not self.currency_template_id:
            return
        self.currency_note = self.currency_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.currency_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.currency_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)
            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.currency_note_image = image

    @api.onchange('price_fee_id')
    def onchange_price_fee_template_id(self):
        if not self.price_fee_id:
            return
        self.price_fee_note = self.price_fee_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.price_fee_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.price_fee_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.price_fee_note_image = image

    @api.onchange('taxation_template_id')
    def onchange_taxation_template_id(self):
        if not self.taxation_template_id:
            return
        self.taxation_note = self.taxation_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.taxation_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.taxation_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.taxation_note_image = image

    @api.onchange('payment_template_id')
    def onchange_payment_template_id(self):
        if not self.payment_template_id:
            return
        self.payment_note = self.payment_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.payment_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.payment_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.payment_note_image = image

    @api.onchange('acceptance_template_id')
    def onchange_acceptance_template_id(self):
        if not self.acceptance_template_id:
            return
        self.acceptance_note = self.acceptance_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.acceptance_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.acceptance_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.acceptance_note_image = image

    @api.onchange('obligation_template_id')
    def onchange_obligation_template_id(self):
        if not self.obligation_template_id:
            return
        self.obligation_note = self.obligation_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.obligation_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.obligation_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.obligation_note_image = image

    @api.onchange('contract_template_id')
    def onchange_contract_template_id(self):
        if not self.contract_template_id:
            return
        self.contract_note = self.contract_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.contract_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.contract_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.contract_note_image = image

    @api.onchange('termination_template_id')
    def onchange_termination_template_id(self):
        if not self.termination_template_id:
            return
        self.termination_note = self.termination_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.termination_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.termination_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)
            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.termination_note_image = image

    @api.onchange('arbitration_template_id')
    def onchange_arbitration_template_id(self):
        if not self.arbitration_template_id:
            return
        self.arbitration_note = self.arbitration_template_id.descrption

        def getSize(txt, font):
            testImg = Image.new('RGB', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            return testDraw.textsize(txt, font)

        if self.arbitration_note:
            fontname = '/odoo/custom/addons/ideatime_customization/zawgyi.ttf'
            fontsize = 14
            colorText = "black"
            colorOutline = "white"
            colorBackground = "white"
            text = convert(self.arbitration_note, 'unicode', 'zawgyi')

            font = ImageFont.truetype(fontname, fontsize)
            width, height = getSize(text, font)

            img = Image.new('RGB', (width + 4, height + 4), colorBackground)
            d = ImageDraw.Draw(img)
            d.text((5, height / 5), text, fill=colorText, font=font)
            d.rectangle((0, 0, width + 5, height + 5), outline=colorOutline)
            img.save('/odoo/custom/addons/sample_image.jpg', 'JPEG')
            with open("/odoo/custom/addons/sample_image.jpg", "rb") as imageFile:
                image = base64.b64encode(imageFile.read())
                self.arbitration_note_image = image

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['project_id'] = self.project_id.id
        return res

    def compute_so_line_amount(self):
        amt = 0
        for so_line in self.order_line:
            dir_mat_amt = 0
            if so_line.order_line_parta_cost_ids:
                for direct_mat_order_line in so_line.order_line_parta_cost_ids:
                    dir_mat_amt += direct_mat_order_line.qty * direct_mat_order_line.unit_price

            amt += dir_mat_amt

        return amt

    def compute_project_cost_estimate(self):
        summary_line = []

        for line in self.order_expense_line:
            if line.display_type:
                summary_line.append({
                    'name': line.name,
                    'qty': 0,
                    'unit': '',
                    'unit_price': 0,
                    'subtotal': 0
                })
            else:
                if summary_line:
                    summary_line[-1]['qty'] += line.product_uom_qty
                    summary_line[-1]['unit'] = line.product_uom_label or ''
                    summary_line[-1]['unit_price'] += line.price_unit
                    summary_line[-1]['subtotal'] += line.price_subtotal

        return summary_line

    def get_sale_order_line(self):
        cost_estimate_array = []

        direct_material_cost = {'sr': '1', 'name': 'Direct material cost', 'data': []}
        indirect_material_cost = {'sr': '2', 'name': 'Indirect material cost', 'data': []}
        direct_labour_cost = {'sr': '3', 'name': 'Direct labour cost', 'data': []}
        thirdparty_contractor_cost = {'sr': '4', 'name': 'Thirdparty cost (Contractor)', 'data': []}
        thirdparty_subcontractor_cost = {'sr': '5', 'name': 'Thirdparty cost (Subcontractor)', 'data': []}

        get_direct_material = self.env['direct.material.cost'].search([('so_line_id', 'in', self.order_line.ids)])
        get_indirect_material = self.env['in.direct.material.cost'].search([('so_line_id', 'in', self.order_line.ids)])
        get_direct_labour_cost = self.env['direct.labour.cost'].search([('so_line_id', 'in', self.order_line.ids)])
        get_thirdparty_contractor_cost = self.env['thirdparty.cost.contractor'].search(
            [('so_line_id', 'in', self.order_line.ids)])
        get_thirdparty_subcontractor_cost = self.env['thirdparty.cost.subcontractor'].search(
            [('so_line_id', 'in', self.order_line.ids)])

        to_group_array = {
            'direct_material_cost': get_direct_material,
            'indirect_material_cost': get_indirect_material,
            'direct_labour_cost': get_direct_labour_cost,
            'thirdparty_contractor_cost': get_thirdparty_contractor_cost,
            'thirdparty_subcontractor_cost': get_thirdparty_subcontractor_cost
        }

        for key, value in to_group_array.items():
            item_no = 1
            group_by_product = {}
            for k, g in groupby(value, lambda x: x.product_id):
                if k in group_by_product:
                    group_by_product[k].extend(list(g))
                else:
                    group_by_product[k] = list(g)
            for item_key, item_value in group_by_product.items():
                data_dict = {
                    'no': item_no,
                    'item_name': item_key.name,
                    'item_code': item_key.barcode
                }
                for attr_val in item_key.product_template_attribute_value_ids:
                    data_dict['item_name'] += ' ' + attr_val.name
                total_qty = 0
                unit_price = 0
                unit = ''
                for grouped_product in item_value:
                    total_qty += grouped_product.qty
                    uom = grouped_product.product_uom_label or ''
                    unit_price = grouped_product.unit_price
                data_dict['qty'] = total_qty
                data_dict['unit'] = uom
                data_dict['price'] = unit_price
                data_dict['total_amount'] = total_qty * unit_price

                eval(key)['data'].append(data_dict)
                item_no += 1

        cost_estimate_array.append(direct_material_cost)
        cost_estimate_array.append(indirect_material_cost)
        cost_estimate_array.append(direct_labour_cost)
        cost_estimate_array.append(thirdparty_contractor_cost)
        cost_estimate_array.append(thirdparty_subcontractor_cost)

        return cost_estimate_array

    def display_type_check(self, order_line):
        if order_line.display_type == 'line_section':
            return False
        else:
            return True

    def action_delivery_direct_mat_product(self):
        for order in self:
            for order_line in order.order_line:
                if (order_line.product_id.is_sale_item):
                    order_line.order_line_parta_cost_ids._action_launch_stock_rule()

        return

    def get_column_name(self):
        column_name = []

        for so_line in self.order_line:
            if so_line.product_id:
                if so_line.column_product and so_line.product_id.name not in column_name:
                    column_name.append(so_line.product_id.name)
        return column_name

    def get_so_line(self):
        column_name = self.get_column_name()
        data = {'column_group': [],
                'other_group': []}

        current_session = ''
        session_data = {}

        for order_line in self.order_line:
            if order_line.display_type == 'line_section':
                current_session = order_line.name
                session_data[current_session] = {
                    'site_id': '',
                    'store_name': current_session,
                    'location': '',
                    'existing': '',
                    'plan': '',
                    'size': '',
                    'area': '',
                    'col_data': [' '] * len(column_name),
                    'total_amt': 0,
                    'remark': ''
                }
            else:
                if order_line.column_product:
                    index = column_name.index(order_line.product_id.name)
                    session_data[current_session]['col_data'][index] = order_line.price_subtotal

                    if not session_data[current_session]['site_id']:
                        session_data[current_session]['site_id'] = order_line.title1
                    if not session_data[current_session]['location']:
                        session_data[current_session]['location'] = order_line.title2
                    if not session_data[current_session]['existing']:
                        session_data[current_session]['existing'] = order_line.title3
                    if not session_data[current_session]['plan']:
                        session_data[current_session]['plan'] = order_line.title4
                    if not session_data[current_session]['size']:
                        session_data[current_session]['size'] = order_line.size
                    if not session_data[current_session]['area']:
                        session_data[current_session]['area'] = order_line.title6
                    session_data[current_session]['total_amt'] += order_line.price_subtotal
                    if not session_data[current_session]['remark']:
                        session_data[current_session]['remark'] = order_line.remark
                else:
                    data['other_group'].append(
                        [order_line.product_id.name, order_line.remark, order_line.price_subtotal])

        for key, value in session_data.items():
            if session_data[key]['col_data'] != [' '] * len(column_name):
                data['column_group'].append(session_data[key])

        samsung_data = {'column_name': column_name, 'line_data': data}

        return samsung_data


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')

    reference_photo = fields.Binary()
    title1 = fields.Text(string="Title1")
    title2 = fields.Text(string="Title2")
    title3 = fields.Text(string="Title3")
    title4 = fields.Text(string="Title4")
    title5 = fields.Text(string="Title5")
    title6 = fields.Text(string="Title6")
    title7 = fields.Text(string="Title7")
    title8 = fields.Text(string="Title8")
    title9 = fields.Text(string="Title9")
    title10 = fields.Text(string="Title10")
    item_order_confirm_ids = fields.One2many('item.order.confirm.line', 'so_line_id')
    client_demand_ids = fields.One2many('order.client.demand.line', 'so_line_id')
    order_line_direct_material_cost_ids = fields.One2many('direct.material.cost', 'so_line_id')

    calculator_line_ids = fields.One2many('calculator.line', 'so_line_id', copy=True)

    size = fields.Char('Size/Service Specification')
    particular_ids = fields.Many2one('material.particular')
    state = fields.Selection(string='Status', related='order_id.state')
    agreement_confirm = fields.Boolean(related='order_id.agreement_confirm')
    material_cost_confirm = fields.Boolean(related='order_id.material_cost_confirm')

    remark = fields.Char(string="Remark", default="N/A")
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict')
    product_uom_label = fields.Char()
    is_contract_client = fields.Boolean(related="order_id.is_contract_client")
    column_product = fields.Boolean(string="Column Product")
    volume_weight_total = fields.Float(compute="_compute_volume_weight_total", string="Total")

    @api.depends('calculator_line_ids')
    def _compute_volume_weight_total(self):
        for record in self:
            for line in record.calculator_line_ids:
                record.volume_weight_total += line.volume_weight
            record.product_uom_qty = record.volume_weight_total

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0
            vals['product_uom_label'] = self.product_id.uom_id.uom_label

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            uom_label=self.product_uom.id
        )

        vals.update(name=product.name, product_uom_label=product.uom_id.uom_label)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        if product.sale_line_warn != 'no-message':
            if product.sale_line_warn == 'block':
                self.product_id = False

            return {
                'warning': {
                    'title': _("Warning for %s", product.name),
                    'message': product.sale_line_warn_msg,
                }
            }

    def calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_sale.view_sale_order_line_cbm_calc').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def open_order_agreement(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_sale.view_order_agreement_line').id

        return {
            'name': _('Additional Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def open_material_cost(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_sale.view_material_cost_line').id

        return {
            'name': _('Material Cost Information'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_procurement_group_vals(self):
        res = super(SaleOrderLine, self)._prepare_procurement_group_vals()
        res['project_id'] = self.order_id.project_id.id
        return res
