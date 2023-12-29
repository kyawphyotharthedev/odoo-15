from odoo import models, fields, api, _


class RequestInfo(models.Model):
    _name = 'request.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Request Info'

    name = fields.Char(related='document_management_id.name')
    date = fields.Date()
    document_number = fields.Char()
    version = fields.Char()
    summary = fields.Text()
    document_management_id = fields.Many2one('document.management')
    request_date = fields.Date(default=fields.Date.today())
    request_type_id = fields.Many2one('request.type')
    analysis_review = fields.Char()
    suggestion = fields.Char()
    audit_review = fields.Char()
    level_statement = fields.Many2one('level.statement', string="Level of statement")
    internal_pic_id = fields.One2many('internal.pic.info', 'request_info_id', tracking=True)
    request_info_appendix_id = fields.One2many('info.appendix', 'request_info_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request_by', 'Submit By'),
        ('audit_by', 'Audit By'),
        ('approved_by', 'Approved By'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='draft')

    def open_request_info(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_document_management.request_info_detail_view').id

        return {
            'name': _('Internal Data New/ Edition Request Info'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'request.info',
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

    def action_cancel_by(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})


class Appendix(models.Model):
    _name = 'info.appendix'
    _description = 'Info Appendix'

    particular = fields.Char()
    upload_file = fields.Binary(string='Upload(File must not exceeded 25MB)')
    url = fields.Char(string="Url(If file size exceeded more than 25MB)")

    request_info_id = fields.Many2one('request.info')
    approve_info_id = fields.Many2one('approval.info')


class InternalPICInfo(models.Model):
    _name = 'internal.pic.info'
    _description = 'Internal PIC Info'

    user_id = fields.Many2one('res.users')
    emp_id = fields.Char(string="Employee ID", related="user_id.emp_id")
    job_position = fields.Char(string="Job Position", related="user_id.job_position")
    employee_email = fields.Char(string="Email", related="user_id.email")
    contact_number = fields.Char(string="Contact Number", related="user_id.contact_number")
    request_info_id = fields.Many2one('request.info')
    approve_info_id = fields.Many2one('approval.info')


class LevelStatement(models.Model):
    _name = 'level.statement'
    _description = 'Level Statement'

    name = fields.Char()
