from odoo import models, fields, api


class SupplierPIC(models.Model):
    _name = 'supplier.pic'
    _description = 'Supplier PIC'

    partner_id = fields.Many2one('res.partner', string="Supplier Name", domain=[('supplier', '=', True)])
    pic_id = fields.Many2one('res.partner', string="PIC Name")
    responsibile_id = fields.Many2one('pic.responsibile', string="Responsibilities")
    remark = fields.Text()
    phoneno = fields.Char()
    position = fields.Char()
    business_type = fields.Text(string="Business Type")
    project_supplier_pic_id = fields.Many2one('project.project')

    @api.onchange('pic_id')
    def onchange_pic_id(self):
        result = {}
        if not self.partner_id:
            return result
        if self.pic_id.function:
            self.position = self.pic_id.function

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        result = {}
        if not self.partner_id:
            return result

        self.remark = self.partner_id.comment
        self.phoneno = self.partner_id.phone or self.partner_id.mobile
        if self.partner_id.phone and self.partner_id.mobile:
            self.phoneno = self.partner_id.phone + ',' + self.partner_id.mobile

        # self.position=self.pic_id.function
        # print( self.position)
        if self.partner_id.industry_type_id or self.partner_id.business_group_id or self.partner_id.business_type_id:
            self.business_type = self.partner_id.industry_type_id.name + '/' + self.partner_id.business_group_id.name + '/' + self.partner_id.business_type_id.name

    def open_supplier_pic(self):
        tree_view_id = self.env.ref('ideatime_core.ideatime_view_partner_tree').id
        form_view_id = self.env.ref('ideatime_core.ideatime_view_partner_address_form').id

        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Supplier'),
            'res_model': 'res.partner',
            'domain': [('id', '=', self.pic_id.id)],
        }

        return action


class ClientPIC(models.Model):
    _name = 'client.pic'
    _description = 'Client PIC'

    partner_id = fields.Many2one('res.partner', related="project_client_pic_id.partner_id",
                                 domain=[('customer', '=', True)])
    pic_id = fields.Many2one('res.partner', string="PIC Name")
    responsibile_id = fields.Many2one('pic.responsibile', string="Responsibilities")
    remark = fields.Text()
    phoneno = fields.Char()
    position = fields.Char()
    project_client_pic_id = fields.Many2one('project.project')
    meeting_mins_record_id = fields.Many2one('meeting.minutes.record')
    jo_accept_id = fields.Many2one('jo.acceptance')
    jo_partner_id = fields.Many2one('res.partner', string='JO Partner', related="jo_accept_id.partner_id", domain=[('customer', '=', True)])
    jo_meeting_partner_id = fields.Many2one('res.partner', string='JO Meeting Partner', related="meeting_mins_record_id.partner_id",
                                            domain=[('customer', '=', True)])

    @api.onchange('pic_id')
    def onchange_pic_id(self):
        self.remark = self.pic_id.comment
        self.phoneno = self.pic_id.phone or self.pic_id.mobile
        if self.pic_id.phone and self.pic_id.mobile:
            self.phoneno = self.pic_id.phone + ',' + self.pic_id.mobile

        self.position = self.pic_id.function

    def open_client_pic(self):
        tree_view_id = self.env.ref('ideatime_core.ideatime_view_partner_tree').id
        form_view_id = self.env.ref('ideatime_core.ideatime_view_partner_address_form').id

        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Customer'),
            'res_model': 'res.partner',
            'domain': [('id', '=', self.pic_id.id)]
        }

        return action


class InternalPIC(models.Model):
    _name = 'internal.pic'
    _description = 'Internal PIC'

    partner_id = fields.Many2one('res.partner', string="PIC Name")
    responsibile_id = fields.Many2one('pic.responsibile', string="Responsibilities")
    remark = fields.Text()
    phoneno = fields.Char()
    position = fields.Char()
    project_internal_pic_id = fields.Many2one('project.project')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        result = {}
        if not self.partner_id:
            return result

        self.remark = self.partner_id.comment
        self.phoneno = self.partner_id.phone or self.partner_id.mobile
        if self.partner_id.phone and self.partner_id.mobile:
            self.phoneno = self.partner_id.phone + ',' + self.partner_id.mobile

        self.position = self.partner_id.function

    def open_internal_pic(self):
        tree_view_id = self.env.ref('ideatime_core.ideatime_view_partner_tree').id
        form_view_id = self.env.ref('ideatime_core.ideatime_view_partner_address_form').id

        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Internal PIC'),
            'res_model': 'res.partner',
            'domain': [('id', '=', self.partner_id.id)],
        }
        return action


class PicResponsible(models.Model):
    _name = "pic.responsibile"
    _description = "PIC Responsible"

    name = fields.Char(string="Name")
