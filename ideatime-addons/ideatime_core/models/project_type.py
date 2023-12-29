from datetime import datetime

from odoo import fields, models, api, _


class ProjectType(models.Model):
    _name = 'project.type'
    _inherit = ['ideatime.board.group']
    _description = 'Project Type'

    name = fields.Char("Name", index=True, required=True, tracking=True)
    active = fields.Boolean(default=True,
                            help="If the active field is set to False, it will allow you to hide the project without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.")
    sequence_id = fields.Many2one('ir.sequence', string='Generate Sequence')

    project_ids = fields.One2many('project.project', 'proj_type_id', string='Projects')
    template_project_id = fields.Many2one('project.project', string='Template Project',
                                          domain=[('is_template', '=', True)])
    left_id = fields.Many2one('project.type')
    right_ids = fields.One2many('project.type', 'left_id')

    project_count = fields.Integer(compute='_compute_count', string="Project Count")
    type_count = fields.Integer(compute='_compute_count', string="Type Count")
    color = fields.Integer(string='Color Index')

    count_project_pending = fields.Integer(compute='_compute_count')
    count_project_doing = fields.Integer(compute='_compute_count')
    count_project_late = fields.Integer(compute='_compute_count')
    count_project_complete = fields.Integer(compute='_compute_count')

    union_proj_type_project_ids = fields.Many2many('project.project', compute="_compute_union_proj_type_project_ids")
    display_name = fields.Char(compute='_compute_display_name', store=True, recursive=True)
    children = fields.Many2many('project.type', compute='_compute_all_hierarchy')
    parent_types = fields.Many2many('project.type', compute='_compute_all_hierarchy')

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    def _compute_all_hierarchy(self):
        for record in self:
            record.children = self.env['project.type']
            record.parent_types = self.env['project.type']
            for child in record.right_ids:
                record.children |= child.children + child
            if record.left_id:
                record.parent_types |= record.left_id + record.left_id.parent_types

    @api.depends('name', 'left_id.display_name')
    def _compute_display_name(self):
        for rec in self:
            if rec.left_id:
                rec.display_name = '%s / %s' % (rec.left_id.display_name, rec.name)
            else:
                rec.display_name = rec.name

    def _add_allowed_users_to_left_id(self):
        for record in self:
            allowed_users = self.env['res.users']
            if record.left_id:
                for same_level_type in record.left_id.right_ids:
                    allowed_users |= same_level_type.allowed_user_ids
                record.left_id.allowed_user_ids = allowed_users

    @api.model
    def create(self, vals):
        res = super(ProjectType, self).create(vals)
        res._add_board_users_to_allowed_uids()
        res._add_allowed_users_to_left_id()
        return res

    def write(self, vals):
        res = super(ProjectType, self).write(vals)
        self._add_board_users_to_allowed_uids()
        self._add_allowed_users_to_left_id()
        return res

    def _compute_union_proj_type_project_ids(self):
        def get_child_projects(proj_types, project):
            for proj_type in proj_types:
                if proj_type.right_ids:
                    return get_child_projects(proj_type.right_ids, project)
                else:
                    if self.env.user.has_group('project.group_project_manager'):
                        project += proj_type.project_ids
                    elif self.env.user.has_group('project.group_project_user'):
                        for proj_record in proj_type.project_ids:
                            if self.env.user in proj_record.internal_user_id or self.env.user == proj_record.user_id:
                                project += proj_record
            return project

        for rec in self:
            project_obj = self.env['project.project']
            child_projects = get_child_projects(rec, project_obj)
            rec.union_proj_type_project_ids = child_projects

    def _compute_count(self):
        for record in self:
            type_data = self.env['project.type'].search([('left_id', '=', record.id)])
            record.type_count = len(type_data)
            if record.right_ids:
                record.project_count = len(record.project_ids)
            else:
                record.project_count = len(record.union_proj_type_project_ids)

            record.count_project_pending = len(record.union_proj_type_project_ids.filtered(
                lambda r: r.proj_type_stage_id == self.env.ref(
                    'ideatime_core.project_type_stage_01_task_stage')))
            record.count_project_doing = len(record.union_proj_type_project_ids.filtered(
                lambda r: r.proj_type_stage_id == self.env.ref(
                    'ideatime_core.project_type_stage_02_task_stage')))
            record.count_project_complete = len(record.union_proj_type_project_ids.filtered(
                lambda r: r.proj_type_stage_id == self.env.ref(
                    'ideatime_core.project_type_stage_03_task_stage')))
            record.count_project_late = len(record.union_proj_type_project_ids.filtered(
                lambda r: r.due_date < datetime.now().date() if r.due_date else False))

    def get_kanbanview_id(self, arg=None):
        if arg:
            if arg['view_route'] == 'project':
                return {'name': self.env.ref('ideatime_project.act_project_project').name,
                        'id': self.env.ref('ideatime_project.act_project_project').id,
                        'model': self.env.ref('ideatime_project.act_project_project').res_model,
                        'xml_id': 'ideatime_project.act_project_project',
                        'kanban': self.env.ref('ideatime_project.idea_project_view').id
                        }

            elif arg['view_route'] == 'type':
                return {'name': self.env.ref('ideatime_project.act_project_type_all').name,
                        'id': self.env.ref('ideatime_project.act_project_type_all').id,
                        'model': self.env.ref('ideatime_project.act_project_type_all').res_model,
                        'xml_id': 'ideatime_project.act_project_type_all',
                        'kanban': False
                        }

    def get_action_project_pending(self):
        view_id = self.env.ref('ideatime_project.idea_project_view').id
        domain = [
            ('proj_type_stage_id', '=', self.env.ref('ideatime_project.project_type_stage_01_task_stage').id),
            ('is_template', '=', False)]
        if self.right_ids:
            domain.append(('id', 'in', self.union_proj_type_project_ids.ids))
        else:
            domain.append(('proj_type_id', '=', self.id))
        return {
            'name': _('Pending Projects'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'context': {'default_proj_type_id': self.id},
            'domain': domain,
            'target': 'current',
            'views': [[view_id, 'kanban'], [False, 'tree'], [False, 'form']],
        }

    def get_action_project_doing(self):
        view_id = self.env.ref('ideatime_project.idea_project_view').id
        domain = [
            ('proj_type_stage_id', '=', self.env.ref('ideatime_core.project_type_stage_02_task_stage').id),
            ('is_template', '=', False)]
        if self.right_ids:
            domain.append(('id', 'in', self.union_proj_type_project_ids.ids))
        else:
            domain.append(('proj_type_id', '=', self.id))
        return {
            'name': _('Doing Projects'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'context': {'default_proj_type_id': self.id},
            'domain': domain,
            'target': 'current',
            'views': [[view_id, 'kanban'], [False, 'tree'], [False, 'form']],
        }

    def get_action_project_late(self):
        view_id = self.env.ref('ideatime_project.idea_project_view').id
        domain = [('is_template', '=', False), ('due_date', '<', datetime.now().date())]
        if self.right_ids:
            domain.append(('id', 'in', self.union_proj_type_project_ids.ids))
        else:
            domain.append(('proj_type_id', '=', self.id))
        return {
            'name': _('Late Projects'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'context': {'default_proj_type_id': self.id},
            'domain': domain,
            'target': 'current',
            'views': [[view_id, 'kanban'], [False, 'tree'], [False, 'form']],
        }

    def get_action_project_complete(self):
        view_id = self.env.ref('ideatime_project.idea_project_view').id
        domain = [
            ('proj_type_stage_id', '=', self.env.ref('ideatime_core.project_type_stage_03_task_stage').id),
            ('is_template', '=', False)]
        if self.right_ids:
            domain.append(('id', 'in', self.union_proj_type_project_ids.ids))
        else:
            domain.append(('proj_type_id', '=', self.id))
        return {
            'name': _('Complete Projects'),
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'context': {'default_proj_type_id': self.id},
            'domain': domain,
            'target': 'current',
            'views': [[view_id, 'kanban'], [False, 'tree'], [False, 'form']],
        }

    def action_project_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ideatime_project.act_project_project_user")
        if self.env.user.has_group('project.group_project_manager'):
            action = self.env["ir.actions.actions"]._for_xml_id("ideatime_project.act_project_project")
        return action
