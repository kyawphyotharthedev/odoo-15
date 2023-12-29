from odoo import fields, models, api, SUPERUSER_ID


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    def _get_project_type_default_stage_id(self):
        """ Gives default stage_id """
        proj_type_id = self.env.context.get('default_proj_type_id')
        if not proj_type_id:
            return False
        return self.stage_find(proj_type_id, [('fold', '=', False)])

    project_site = fields.Char('Project Site')
    finance_senior_management_id = fields.Many2one('res.users')
    project_senior_management_id = fields.Many2one('res.users')
    director = fields.Many2one('res.users', string="Project Director")
    picking_ids = fields.One2many('stock.picking', 'project_id', string='Pickings')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    proj_type_stage_id = fields.Many2one('project.task.type', string='Project Type Stage', ondelete='restrict',
                                         tracking=True, index=True,
                                         default=_get_project_type_default_stage_id,
                                         group_expand='_read_project_type_group_stage_ids',
                                         domain="[('project_type_ids', '=', proj_type_id)]", copy=False)
    is_contract_client = fields.Boolean(default=False)
    cate_sector_id = fields.Many2one('service.category.sector', string='Service Sector')
    cate_line_id = fields.Many2one('service.category.line', string='Service Line')
    manual_project_name = fields.Char(string="Manual Project Name")
    proj_type_id = fields.Many2one('project.type', string='Project Type')

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(order.picking_ids)

    @api.model
    def _read_project_type_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_proj_type_id' in self.env.context:
            search_domain = ['|', ('project_type_ids', '=', self.env.context['default_proj_type_id'])] + search_domain
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def stage_find(self, section_id, domain=None, order='sequence'):
        # collect all section_ids
        if domain is None:
            domain = []
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('proj_type_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_type_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id


class ProjectDirectMaterialCost(models.Model):
    _name = 'projectdir.material.cost'
    _description = 'Project Direct Material Cost'

    project_direct_move_ids = fields.One2many('stock.move', 'projectdir_line_id', string='Stock Moves')


class ProjectInDirectMaterialCost(models.Model):
    _name = 'projectindir.material.cost'
    _description = 'Project InDirect Material Cost'

    project_indirect_move_ids = fields.One2many('stock.move', 'projectindir_line_id', string='Stock Moves')
