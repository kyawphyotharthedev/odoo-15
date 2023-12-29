from odoo import api, fields, models
import pytz


class MailActivityInherit(models.Model):
    _inherit = 'mail.activity'

    inform_date = fields.Datetime(string="Inform Date", default=lambda self: fields.datetime.now())
    temp_date_deadline = fields.Datetime(default=None)
    custom_date_deadline = fields.Datetime()
    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default='', index=True, required=True)
    date_deadline = fields.Date('Due Date', index=True, required=True, default=None)

    @api.onchange('temp_date_deadline')
    def _set_date_deadline(self):
        if self.temp_date_deadline:
            self.date_deadline = self.temp_date_deadline.date()
            if self.env.user.tz:
                tz = pytz.timezone(self.env.user.tz)
            else:
                tz = pytz.timezone('Asia/Yangon')
            self.custom_date_deadline = self.temp_date_deadline.replace(tzinfo=pytz.timezone('UTC')).astimezone(
                tz).replace(tzinfo=None)
