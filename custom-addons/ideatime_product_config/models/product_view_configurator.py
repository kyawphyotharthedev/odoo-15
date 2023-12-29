from odoo import models, fields, api


class ProductConfigurator(models.Model):
    _inherit = "product.template"
    _check_company_auto = True
    company_id = fields.Many2one('res.company', 'Company', index=1,
                                 store=True, default=lambda self: self.env.company)
