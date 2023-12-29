from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = "stock.picking"
    # carrier_tracking_ref =field.Char(string="Tracking Ref")

    def do_print_picking_issue(self):
        self.write({'printed': True})
        return self.env.ref('ideatime_stock.action_report_goods_issue').report_action(self)

    def do_print_picking_receive(self):
        self.write({'printed': True})
        return self.env.ref('ideatime_stock.action_report_goods_received').report_action(self)
