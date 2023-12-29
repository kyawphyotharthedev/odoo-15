from odoo import models, fields
from datetime import datetime


class ItemSamplePhotoLine(models.Model):
    _name = 'item.sample.photo.line'
    _description = 'Item Sample Photo Line'

    product_id = fields.Many2one('product.template')
    sample_photo = fields.Binary(string='Sample Photo')
    file_name = fields.Char("File Name")


class MaterialSamplePhotoLine(models.Model):
    _name = 'material.sample.photo.line'
    _description = 'Material Sample Photo Line'

    product_id = fields.Many2one('product.template')
    sample_photo = fields.Binary(string='Sample Photo')
    file_name = fields.Char("File Name")


class ProcessInstallPhotoLine(models.Model):
    _name = 'process_install.sample.photo.line'
    _description = 'Process Install Sample Photo Line'

    product_id = fields.Many2one('product.template')
    sample_photo = fields.Binary(string='Sample Photo')
    file_name = fields.Char("File Name")


class ItemIntro(models.Model):
    _name = 'item.intro'
    _description = 'Item Intro'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class MOQ(models.Model):
    _name = 'min.of.qty'
    _description = 'Min Of Qty'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class ProductEnvQualityStd(models.Model):
    _name = 'product.env_quality_std'
    _description = 'Product Env Quality Std'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class OtherSupplementInfo(models.Model):
    _name = 'other.supplement.info'
    _description = 'Other Supplement Info'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


# Item Specification

class ItemSpecification(models.Model):
    _name = 'item.spec'
    _description = 'Item Specification'

    sequence = fields.Integer(string='Sequence', default=10)

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Many2one('item.spec.particular', string='Particular')
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')
    name = fields.Char()
    display_type = fields.Selection([
        ('line_section', "Section"), ('line_title_section', "Title Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    item_spec_part_title_id = fields.Many2one('item.spec.particular.title')


class ItemQuality(models.Model):
    _name = 'item.quality'
    _description = 'Item Quality'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class WarrentyPeriod(models.Model):
    _name = 'warrenty.period'
    _description = 'Warrenty Period'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class WarrentyFactor(models.Model):
    _name = 'warrenty.factor'
    _description = 'Warrenty Factor'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class MainMaterialSpec(models.Model):
    _name = 'main.material.spec'
    _description = 'Main Material Spec'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class SupportMaterialSpec(models.Model):
    _name = 'support.material.spec'
    _description = 'Support Material Spec'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class ProductionCraftInstall(models.Model):
    _name = 'production.craft.install'
    _description = 'Production Craft Install'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class ProductionProcess(models.Model):
    _name = 'production.process'
    _description = 'Production Process'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    sample_photo = fields.Binary(string='Sample Photo')
    file_name = fields.Char("File Name")
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class InstallationProcess(models.Model):
    _name = 'installation.process'
    _description = 'Installation Process'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    description = fields.Text('Description')
    sample_photo = fields.Binary(string='Sample Photo')
    file_name = fields.Char("File Name")
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class MaterialQCProcess(models.Model):
    _name = 'material.qc.process'
    _description = 'Material QC Process'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string='Particular')
    standard_type = fields.Text('Standard Type')
    standard_sample_photo = fields.Binary(string='Standard Sample Photo')
    standard_file_name = fields.Char("Std File Name")
    prohibited_type = fields.Text('Prohibited Type')
    prohibited_sample_photo = fields.Binary(string='Prohibited Sample Photo')
    prohibited_file_name = fields.Char("Prohibited File Name")
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class ProductionQCProcess(models.Model):
    _name = 'production.qc.process'
    _description = 'Production QC Process'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string='Particular')
    standard_type = fields.Text('Standard Type')
    standard_sample_photo = fields.Binary(string='Standard Sample Photo')
    standard_file_name = fields.Char("Std File Name")
    prohibited_type = fields.Text('Prohibited Type')
    prohibited_sample_photo = fields.Binary(string='Prohibited Sample Photo')
    prohibited_file_name = fields.Char("Prohibited File Name")
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class InstallationQCProcess(models.Model):
    _name = 'installation.qc.process'
    _description = 'Installation QC Process'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    standard_type = fields.Text('Standard Type')
    standard_sample_photo = fields.Binary(string='Standard Sample Photo')
    standard_file_name = fields.Char("Std File Name")
    prohibited_type = fields.Text('Prohibited Type')
    prohibited_sample_photo = fields.Binary(string='Prohibited Sample Photo')
    prohibited_file_name = fields.Char("Prohibited File Name")
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class ServiceQCProcess(models.Model):
    _name = 'service.qc.process'
    _description = 'Service QC Process'

    product_id = fields.Many2one('product.template', string='Product')
    particular_id = fields.Char(string="Particular")
    standard_type = fields.Text('Standard Type')
    standard_sample_photo = fields.Binary(string='Standard Sample Photo')
    standard_file_name = fields.Char("Std File Name")
    prohibited_type = fields.Text('Prohibited Type')
    prohibited_sample_photo = fields.Binary(string='Prohibited Sample Photo')
    prohibited_file_name = fields.Char("Prohibited File Name")
    product_attr_id = fields.Many2one('product.attribute', string="Attribute")
    product_attr_val_id = fields.Many2many('product.attribute.value', string='Attribute Values',
                                           domain="[('attribute_id', '=', product_attr_id)]")
    product_ids = fields.Many2many('product.product', string='Products')


class BEPSaleTarget(models.Model):
    _name = 'bep.sale.target'
    _description = 'BEP Sale Target'

    def _get_year(self):
        rslt = []
        for x in range((datetime.now().year) - 1, (datetime.now().year) + 3):
            rslt.append((str(x), str(x)))

        return rslt

    product_id = fields.Many2one('product.template', string='Product')
    year = fields.Selection(selection=_get_year, string='Year')
    target_qty = fields.Float('Target Qty')
    target_amount = fields.Float('Target Amount')
    bep_file = fields.Binary(string='Document')
    bep_file_name = fields.Char("File Name")
