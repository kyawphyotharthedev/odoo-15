from odoo import models, fields


class ItemIntroParticular(models.Model):
    _name = 'item.intro.particular'
    _description = 'Item Intro Particular'

    name = fields.Char('Name')


class MOQParticular(models.Model):
    _name = 'min.of.qty.particular'
    _description = 'Min of Qty Particular'

    name = fields.Char('Name')


class ProductEnvQualityStdParticular(models.Model):
    _name = 'product.env_quality_std.particular'
    _description = 'Product Env Quality Std Particular'

    name = fields.Char('Name')


class OtherSupplementInfoParticular(models.Model):
    _name = 'other.supplement.info.particular'
    _description = 'Other Supplement Info Particular'

    name = fields.Char('Name')


class ItemSpecificationParticular(models.Model):
    _name = 'item.spec.particular'
    _order = 'sequence, id'
    _description = 'Item Specification Particular'

    sequence = fields.Integer(string='Sequence', default=10)

    name = fields.Char('Name')


class ItemQualityParticular(models.Model):
    _name = 'item.quality.particular'
    _description = 'Item Quality Particular'

    name = fields.Char('Name')


class WarrentyPeriodParticular(models.Model):
    _name = 'warrenty.period.particular'
    _description = 'Warrenty Period Particular'

    name = fields.Char('Name')


class WarrentyFactorParticular(models.Model):
    _name = 'warrenty.factor.particular'
    _description = 'Warrenty Factor Particular'

    name = fields.Char('Name')


class MainMaterialSpecParticular(models.Model):
    _name = 'main.material.spec.particular'
    _description = 'Main Material Spec Particular'

    name = fields.Char('Name')


class SupportMaterialSpecParticular(models.Model):
    _name = 'support.material.spec.particular'
    _description = 'Support Material Spec Particular'

    name = fields.Char('Name')


class ProductionCraftInstallParticular(models.Model):
    _name = 'production.craft.install.particular'
    _description = 'Production Craft Install Particular'

    name = fields.Char('Name')


class ProductionProcessParticular(models.Model):
    _name = 'production.process.particular'
    _description = 'Production Process Particular'

    name = fields.Char('Name')


class InstallationProcessParticular(models.Model):
    _name = 'installation.process.particular'
    _description = 'Installation Process Particular'

    name = fields.Char('Name')


class MaterialQCProcessParticular(models.Model):
    _name = 'material.qc.process.particular'
    _description = 'Material QC Process Particular'

    name = fields.Char('Name')


class InstallationQCProcessParticular(models.Model):
    _name = 'installation.qc.process.particular'
    _description = 'Installation QC Process Particular'

    name = fields.Char('Name')


class ServiceQCProcessParticular(models.Model):
    _name = 'service.qc.process.particular'
    _description = 'Service QC Process Particular'

    name = fields.Char('Name')


class ClientDemandParticular(models.Model):
    _name = 'client.demand.particular'
    _description = 'Client Demand Particular'

    name = fields.Char('Name')


class ExpensesOrderLineParticular(models.Model):
    _name = 'expense.order.line.particular'
    _description = 'Expenses Order Line Particular'

    name = fields.Char('Name')


class ItemOrderConfirmParticular(models.Model):
    _name = 'item.order.confirm.particular'
    _description = 'Item Order Confirm Particular'

    name = fields.Char('Name')


class ItemSpecParticularTemplate(models.Model):
    _name = 'item.spec.particular.template'
    _order = 'sequence, id'
    _description = 'Item Spec Particular Template'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char('Name', required=True)
    particular_template_line = fields.One2many('item.spec.particular.tmpl.line', 'particular_template_id')


class ItemSpecParticularTemplateLine(models.Model):
    _name = 'item.spec.particular.tmpl.line'
    _order = 'sequence, id'
    _description = 'Item Spec Particular Template Line'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Name')
    particular_id = fields.Many2one('item.spec.particular')
    display_type = fields.Selection([
        ('line_section', "Section"), ('line_title_section', "Title Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    particular_template_id = fields.Many2one('item.spec.particular.template')
    item_spec_part_title_id = fields.Many2one('item.spec.particular.title')


class ItemSpecTitle(models.Model):
    _name = 'item.spec.particular.title'
    _order = 'sequence, id'
    _description = 'Item Spec Particular Title'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char('Name', required=True)
