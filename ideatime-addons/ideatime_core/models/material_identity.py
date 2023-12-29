from odoo import models, fields, api


class MaterialGroup(models.Model):
    _name = 'material.group'
    _description = 'Material Group'

    name = fields.Char(string='Name', required=True)
    right_ids = fields.One2many('material.sector', 'left_id')
    code = fields.Char(string='Code Represent')
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')


class MaterialSector(models.Model):
    _name = 'material.sector'
    _description = 'Material Sector'

    left_id = fields.Many2one('material.group', string='Material Group')
    name = fields.Char(string='Name', required=True)
    right_ids = fields.One2many('material.category', 'left_id', string='Material Category')
    code = fields.Char(string='Code Represent')
    description = fields.Char(
        string='Display Name ', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.name, data.name)
            else:
                data.description = data.name


class MaterialCategory(models.Model):
    _name = 'material.category'
    _order = 'name asc'
    _description = 'Material Category'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.sector')
    right_ids = fields.One2many('material.sub.category', 'left_id', string="Sub Category")
    description = fields.Char(
        'Display Name ', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class MaterialSubCategory(models.Model):
    _name = 'material.sub.category'
    _description = 'Material Sub Category'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.category')
    right_ids = fields.One2many('material.particular', 'left_id', string="Particular")
    description = fields.Char(
        'Display Name ', compute='_compute_dispaly_name',
        store=True)

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class MaterialGrade(models.Model):
    _name = 'material.grade'
    _description = 'Material Grade'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)


class MaterialSubGrade(models.Model):
    _name = 'material.sub.grade'
    _description = 'Material Sub Grade'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)


class MaterialParticular(models.Model):
    _name = 'material.particular'
    _description = 'Material Particular'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.sub.category', required=True)
    right_ids = fields.One2many('material.classification', 'left_id')
    description = fields.Char(
        'Display Name', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class MaterialClassification(models.Model):
    _name = 'material.classification'
    _description = 'Material Classification'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.particular')
    right_ids = fields.One2many('material.type', 'left_id', string="Type")
    description = fields.Char(
        'Display Name ', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class MaterialType(models.Model):
    _name = 'material.type'
    _description = 'Material Type'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.classification')
    right_ids = fields.One2many('material.function', 'left_id', string="Function")
    description = fields.Char(
        'Display Name ', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class MaterialFunction(models.Model):
    _name = 'material.function'
    _description = 'Material Function'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.type', required=True)
    right_ids = fields.One2many('material.steamline', 'left_id')
    description = fields.Char(
        'Display Name ', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class MaterialSteamline(models.Model):
    _name = 'material.steamline'
    _description = 'Material Steamline'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    left_id = fields.Many2one('material.function', required=True)
    description = fields.Char(
        'Display Name ', compute='_compute_dispaly_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')

    @api.depends('name', 'left_id')
    def _compute_dispaly_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name
