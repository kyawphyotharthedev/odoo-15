from odoo import models, fields, api, _


class GroupOneGroup(models.Model):
    _name = 'service.category.group'
    _description = 'Service Category Group'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code Represent', required=True)
    right_ids = fields.One2many('service.category.sector', 'left_id', string='Sectors')
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        res = super(GroupOneGroup, self).create(vals)
        create_seq = self.env['ir.sequence'].create({
            'name': res.name + "'s Childs' Sequence",
            'implementation': 'standard',
            'padding': 0,
            'number_increment': 1,
            'number_next_actual': 1,
        })
        res.update({'seq_id': create_seq.id})
        return res


class GroupOneSector(models.Model):
    _name = 'service.category.sector'
    _description = 'Service Category Sector'

    left_id = fields.Many2one('service.category.group', required=True)
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code Represent')
    description = fields.Char(
        'Display Name ', compute='compute_display_name',
        store=True)

    right_ids = fields.One2many('service.category.line', 'left_id', string='Line')
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')
    active = fields.Boolean(default=True)

    @api.depends('name', 'left_id')
    def compute_display_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.name, data.name)
            else:
                data.description = data.name

    @api.model
    def create(self, vals):
        res = super(GroupOneSector, self).create(vals)
        create_seq = self.env['ir.sequence'].create({
            'name': res.name + "'s Childs' Sequence",
            'implementation': 'standard',
            'padding': 0,
            'number_increment': 1,
            'number_next_actual': 1,
        })
        res.update({'seq_id': create_seq.id, 'code': res.left_id.seq_id.next_by_id()})
        return res


class GroupTwoService(models.Model):
    _name = 'service.category.line'
    _description = 'Service Category Line'

    left_id = fields.Many2one('service.category.sector', required=True)
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code Represent')
    description = fields.Char(
        'Display Name ', compute='compute_display_name',
        store=True)
    right_ids = fields.One2many('service.category.particular', 'left_id', string='Particular')
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')
    active = fields.Boolean(default=True)

    @api.depends('name', 'left_id')
    def compute_display_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name

    @api.model
    def create(self, vals):
        res = super(GroupTwoService, self).create(vals)
        create_seq = self.env['ir.sequence'].create({
            'name': res.name + "'s Childs' Sequence",
            'implementation': 'standard',
            'padding': 0,
            'number_increment': 1,
            'number_next_actual': 1,
        })
        res.update({'seq_id': create_seq.id, 'code': res.left_id.seq_id.next_by_id()})
        return res


class GroupThreeParticular(models.Model):
    _name = 'service.category.particular'
    _description = 'Service Category Particular'

    left_id = fields.Many2one('service.category.line', required=True)
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code Represent')
    description = fields.Char(
        'Display Name ', compute='compute_display_name',
        store=True)
    right_ids = fields.One2many('service.category.function', 'left_id', string='Function')
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')
    active = fields.Boolean(default=True)

    @api.depends('name', 'left_id')
    def compute_display_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class GroupFourFunction(models.Model):
    _name = 'service.category.function'
    _description = 'Service Category Function'

    left_id = fields.Many2one('service.category.particular', required=True)
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code Represent')
    description = fields.Char(
        'Display Name ', compute='compute_display_name',
        store=True)
    right_ids = fields.One2many('service.category.option', 'left_id', string='Option')
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')
    active = fields.Boolean(default=True)

    @api.depends('name', 'left_id')
    def compute_display_name(self):
        for data in self:
            if data.left_id:
                data.description = '%s / %s' % (data.left_id.description, data.name)
            else:
                data.description = data.name


class GroupFiveOption(models.Model):
    _name = 'service.category.option'
    _description = 'Service Category Option'

    left_id = fields.Many2one('service.category.function', required=True)
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code Represent')
    description = fields.Char(
        'Display Name ', compute='compute_display_name',
        store=True)
    seq_id = fields.Many2one('ir.sequence', string='Child Seq')
    is_innovative = fields.Boolean(string='Is Innovative Type', default=False)
    active = fields.Boolean(default=True)

    @api.depends('name', 'left_id')
    def compute_display_name(self):
        for option in self:
            if option.left_id:
                option.description = '%s / %s' % (option.left_id.description, option.name)
            else:
                option.description = option.name


class SaleItemCategory(models.Model):
    _name = 'sale.item.category'
    _description = 'Sale Item Category'

    name = fields.Char(string='Name', required=True)
