from odoo import fields, models


class ProjectSite(models.Model):
    _name = 'project.site'
    _description = 'Project Site'

    name = fields.Char(string="Name", required=True)

    township = fields.Char(string="Township")
    city = fields.Many2one('res.country.state', string="City")
    street = fields.Char(string="Street")
    ward = fields.Char(string="Ward")
    no = fields.Char(string="No:")
    site_building = fields.Char(string="Site Name/building Name")
    tower_type = fields.Char(string="Tower Type")
    tower_no = fields.Char(string="Tower No")
    floor = fields.Char(string="Floor")
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the project without removing it.")
