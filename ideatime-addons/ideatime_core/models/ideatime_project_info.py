from odoo import fields, models


class IndustryType(models.Model):
    _name = "industry.type"
    _description = "Industry Type"

    name = fields.Char('Name', required=True)
    right_ids = fields.One2many('business.group', 'left_id', string='Business Group')


class BusinessGroup(models.Model):
    _name = "business.group"
    _description = "Business Group"

    name = fields.Char('Name', required=True)
    left_id = fields.Many2one('industry.type', required=True, string='Industry Type')
    right_ids = fields.One2many('business.type', 'left_id', string='Business Type')


class BusinessType(models.Model):
    _name = "business.type"
    _description = "Business Type"

    name = fields.Char('Name', required=True)
    left_id = fields.Many2one('business.group', required=True, string='Business Group')


class ServiceChannel(models.Model):
    _name = "service.channel"
    _description = "Service Channel"

    name = fields.Char('Name', required=True)
