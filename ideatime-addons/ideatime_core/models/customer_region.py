from odoo import models, fields


class CustomerRegion(models.Model):
    _name = 'customer.region'
    _description = "Customer Region"

    name = fields.Char(string="Region")
    country_id = fields.Many2one('res.country', string="Country")


class CustomerCity(models.Model):
    _name = 'customer.city'
    _description = "Customer City"

    name = fields.Char(string="City")
    region = fields.Many2one('customer.region', string="Region")


class CustomerTownship(models.Model):
    _name = 'customer.township'
    _description = "Customer Township"

    name = fields.Char(string="Township")
    city = fields.Many2one('customer.city', string="City")
    region = fields.Many2one('customer.region', string="Region")
