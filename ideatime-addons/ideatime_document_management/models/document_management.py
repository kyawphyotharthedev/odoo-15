from odoo import models, fields, api, _


class Function(models.Model):
    _name = 'function'
    _description = 'Function'

    name = fields.Char()


class DocumentType(models.Model):
    _name = 'document.type'
    _description = 'Document Type'

    name = fields.Char()


class PermissionLevel(models.Model):
    _name = 'permission.level'
    _description = 'Permission Level'

    name = fields.Char()


class RelatedDepartment(models.Model):
    _name = 'related.department'
    _description = 'Related Department'

    name = fields.Char()


class RequestType(models.Model):
    _name = 'request.type'
    _description = 'Request Type'

    name = fields.Char()


class DocumentManagement(models.Model):
    _name = 'document.management'
    _description = "Document Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(readonly=True)

    file_name = fields.Char(compute="_compute_file_data")
    update_version_file = fields.Binary(compute="_compute_file_data")
    update_version_file_url = fields.Char(compute="_compute_file_data")
    url = fields.Char(compute="_compute_file_data")
    url_password = fields.Char(compute="_compute_file_data")
    url_show_password = fields.Char(compute="_compute_file_data")
    remark = fields.Text()
    used_policy_template = fields.Binary(string='Used in Policy with Template')
    document_type_id = fields.Many2one('document.type')
    document_name = fields.Char()
    document_number = fields.Char()
    update_version = fields.Char(compute='_compute_file_data')
    description = fields.Text()
    function_id = fields.Many2one('function')
    permission_level_id = fields.Many2many('permission.level')
    job_position_id = fields.Many2many('hr.job', string="Job Position")
    valid_date = fields.Date(compute="_compute_file_data")
    document_lift_time = fields.Char(compute="_compute_file_data")
    review_date = fields.Date(string="Review Date(remaind action)", compute="_compute_file_data")
    related_department_id = fields.Many2many('hr.department')
    check_job_position = fields.Boolean(default=False, compute='_set_check_job_position')

    @api.onchange('related_department_id')
    def _set_check_job_position(self):
        for rec in self:
            if rec.related_department_id:
                rec.check_job_position = True
            else:
                rec.check_job_position = False
                rec.job_position_id = False

    used_business_unit = fields.Char(string="Used in Business Unit")
    used_process = fields.Char(string="Used in Process")
    audit_by = fields.Many2one('res.users')
    approved_by = fields.Many2one('res.users')
    responsible_person = fields.Many2one('res.users')
    request_info_id = fields.One2many('request.info', 'document_management_id')
    approval_info_id = fields.One2many('approval.info', 'document_management_id')
    information = fields.Text()
    show_password = fields.Boolean(compute='_compute_show_password')

    @api.depends('approval_info_id')
    def _compute_show_password(self):
        for record in self:
            record.show_password = False
            for line in record.approval_info_id:
                record.show_password = line.show_password

    @api.onchange('document_name', 'document_number', 'update_version', 'used_process', 'valid_date',
                  'document_lift_time', 'approved_by')
    def _compute_information(self):
        information = []
        for record in self:
            information = ['Document Name:' + str(record.document_name) + '\n' + 'Document Number:' + str(
                record.document_number) + '\n' + 'Update Version:' + str(
                record.update_version) + '\n' + 'Used in Process:' + str(
                record.used_process) + '\n' + 'Valid Date:' + str(
                record.valid_date) + '\n' + 'Document Lift Time:' + str(
                record.document_lift_time) + '\n' + 'Approved By:' + str(record.approved_by.name)]
            record.information = "\n".join(str(x) for x in information)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('document.management') or _('New')
        return super(DocumentManagement, self).create(vals)

    @api.depends('approval_info_id')
    def _compute_file_data(self):
        for record in self:
            record.file_name = ''
            record.update_version = ''
            record.valid_date = False
            record.review_date = False
            record.document_lift_time = ''
            record.update_version_file = False
            record.url = ''
            record.url_show_password = ''
            record.url_password = ''
            for line in record.approval_info_id:
                if line.state == 'action':
                    record.file_name = line[:1].file_name
                    record.update_version = line[:1].update_version
                    record.valid_date = line[:1].valid_date
                    record.review_date = line[:1].review_date
                    record.document_lift_time = line[:1].document_lifttime_id.name
                    record.update_version_file = line[:1].upload
                    if line.url and line.show_password:
                        record.url = line[:1].url
                        record.url_show_password = line[:1].url_show_password
                    elif line.url and not line.show_password:
                        record.url = line[:1].url
                        record.url_password = line[:1].url_password
