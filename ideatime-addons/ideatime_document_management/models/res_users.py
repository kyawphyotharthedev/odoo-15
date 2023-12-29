from odoo import models, fields


class User(models.Model):
    _inherit = 'res.users'

    emp_id = fields.Char(string="Employee ID", related='employee_id.name')
    job_position = fields.Char(string="Employee Job Position", related='employee_id.job_id.name')
    employee_email = fields.Char(string="Employee Email", related='employee_id.work_email')

    def _set_contact_number(self):
        contact_no = ''
        for rec in self:
            if rec.employee_id.mobile_phone:
                contact_no += rec.employee_id.mobile_phone
            if rec.employee_id.mobile_phone and rec.employee_id.work_phone:
                contact_no += ", "
            if rec.employee_id.work_phone:
                contact_no += rec.employee_id.work_phone
            rec.contact_number = contact_no

    contact_number = fields.Char(string="Contact Number", compute='_set_contact_number')
