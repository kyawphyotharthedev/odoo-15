from odoo import models, api, fields


class StockLocationOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    stock_location_ids = fields.Many2many('stock.location', domain=[("reorder_location", "=", True)],
                                          string='Stock Locations')

    @api.depends('product_id', 'location_id', 'product_id.stock_move_ids',
                 'product_id.stock_move_ids.state', 'product_id.stock_move_ids.date',
                 'product_id.stock_move_ids.product_uom_qty', 'stock_location_ids')
    @api.onchange('stock_location_ids')
    def _compute_qty(self):
        for orderpoint in self:
            default_qty = super(StockLocationOrderpoint, orderpoint)._compute_qty()
            orderpoint.qty_on_hand = default_qty

            if orderpoint.stock_location_ids:
                for location in orderpoint.stock_location_ids:
                    location_qty = sum(move.product_uom_qty for move in self.env['stock.move'].search([
                        ('location_dest_id', '=', location.id),
                        ('product_id', '=', orderpoint.product_id.id),
                        ('state', '=', 'done')
                    ]))
                    orderpoint.qty_on_hand += location_qty


