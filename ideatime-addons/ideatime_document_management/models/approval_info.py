from odoo import models, fields, api, _
import datetime


class ApprovalInfo(models.Model):
    _name = 'approval.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Approval Info'

    name = fields.Char(related='document_management_id.name')
    preparation_date = fields.Date(default=fields.Date.today())
    document_number = fields.Char()
    version = fields.Char()
    summary = fields.Text()
    current_version = fields.Char()
    weakness_content = fields.Char()
    update_version = fields.Char()
    update_content = fields.Char()
    file_name = fields.Char(compute="_compute_file_name")
    valid_date = fields.Date()
    review_date = fields.Date(tracking=True, string='Review Date(remaind action)')
    document_lifttime_id = fields.Many2one('document.lifttime', string="Document Lift-Time")
    upload = fields.Binary()
    url = fields.Char()
    url_password = fields.Char()
    url_show_password = fields.Char()
    remark = fields.Text()
    document_management_id = fields.Many2one('document.management')
    info_appendix_id = fields.One2many('info.appendix', 'approve_info_id')
    internal_pic_id = fields.One2many('internal.pic.info', 'approve_info_id')
    show_password = fields.Boolean(default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request_by', 'Submit By'),
        ('audit_by', 'Audit By'),
        ('approved_by', 'Approved By'),
        ('action', 'Action'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='draft')

    file_permission = fields.Selection([
        ('readonly', 'Readonly'),
        ('download', 'download'),
    ], tracking=True, default='readonly')

    @api.onchange('url_password')
    def onchange_url_password(self):
        self.url_show_password = self.url_password

    @api.onchange('url_show_password')
    def onchange_url_show_password(self):
        self.url_password = self.url_show_password

    def open_approval_info(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_document_management.approve_info_detail_view').id

        return {
            'name': _('"Internal Data Approval info'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'approval.info',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'self',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def action_request_by(self):
        if self.state == 'draft':
            self.write({'state': 'request_by'})

    def action_audit_by(self):
        if self.state == 'request_by':
            self.write({'state': 'audit_by'})

    def action_approved_by(self):
        if self.state == 'audit_by':
            self.write({'state': 'approved_by'})

    def action_by(self):
        if self.state == 'approved_by':
            self.write({'state': 'action'})

    def action_cancel_by(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.depends('document_management_id')
    def _compute_file_name(self):
        file_name = []
        for record in self:
            for line in record.document_management_id:
                if line.function_id:
                    file_name.append(str(line.function_id.name))
                if line.document_name:
                    file_name.append(str(line.document_name))
                if line.document_number:
                    file_name.append(str(line.document_number))
                if record.update_version:
                    file_name.append(str(record.update_version))
                record.file_name = "_".join(str(x) for x in file_name)


class DocumentLifttime(models.Model):
    _name = 'document.lifttime'
    _description = 'Document Lift Time'

    name = fields.Char()
