from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ProjectCostEstimatePartB(models.Model):
    _name = 'project.cost.estimate.line'
    _description = 'Project Cost Estimate Line'

    # uom field for  Calculate CBM form
    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')

    product_uom_label = fields.Char()

    particular_ids = fields.Many2one('expense.order.line.particular')
    product_id = fields.Many2one('product.product', string='Product', change_default=True, ondelete='restrict')
    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Volume Weight', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))

    approval_budget_id = fields.Many2one('budget.approval', string='Project Reference', required=True,
                                         ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description')

    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

    cost_estimate = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    remark = fields.Char(string="Remark", default="N/A")

    product_uom_qty = fields.Float(compute="_compute_product_qty", string='Ordered Quantity',
                                   digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"), ('line_expense_section', "Expense Section")], default=False,
        help="Technical field for UX purpose.")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    currency_id = fields.Many2one('res.currency')
    budget_calculator_line = fields.One2many('budget.calculator.line', 'project_cost_estimate_line_id')
    volume_weight_total = fields.Float(compute="_compute_volume_weight_total", string="Total")
    usage_type = fields.Selection(
        [('self', 'Self Purchase'), ('proc', 'Procurement Purchase'), ('deli', 'Stock Delivery')], 'Type',
        default='self')
    batch_check = fields.Boolean()
    budget_batch_line_id = fields.One2many('budget.batch.line', 'budget_partB_id')

    cost_type_id = fields.Many2one('cost.type', string='Cost Type', required=True)

    def create_batch(self):
        batch_lines = []
        for rec in self:

            for record in rec.approval_budget_id:
                if record.budget_line_id:
                    for batch_line in record.budget_line_id:
                        batch_lines.append((0, 0, {
                            'budget_id': batch_line.approval_budget_id.id,
                            'batch_id': batch_line.id,

                        }))

            rec.budget_batch_line_id = batch_lines
            rec.budget_batch_line_id[0]['product_uom_qty'] = rec.product_uom_qty
            rec.budget_batch_line_id[0]['unit_price'] = rec.price_unit
            rec.budget_batch_line_id[0]['total_amount'] = rec.cost_estimate
            rec.batch_check = True

    @api.constrains('budget_batch_line_id')
    def _check_exist_batch_in_line(self):
        for batch in self:
            exist_batch_list = []
            for line in batch.budget_batch_line_id:
                if line.batch_id.id in exist_batch_list:
                    raise ValidationError(_('Batch should be one per line.'))
                exist_batch_list.append(line.batch_id.id)

    @api.depends('budget_calculator_line')
    def _compute_volume_weight_total(self):
        for record in self:
            for line in record.budget_calculator_line:
                record.volume_weight_total += line.volume_weight

    @api.depends('Pcs', 'length', 'width', 'height')
    def _compute_product_qty(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            pcs = 1 if line.Pcs < 1 else line.Pcs
            length = 1 if line.length < 1 else line.length
            width = 1 if line.width < 1 else line.width
            height = 1 if line.height < 1 else line.height

            product_uom_qty = pcs * length * width * height

            line.update({
                'product_uom_qty': product_uom_qty,
            })

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.product_uom_label = self.product_id.uom_id.uom_label
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * line.product_uom_qty

            line.update({
                'cost_estimate': price
            })

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)

        self.product_uom_qty = self.volume_weight
        # self.write({'product_uom_qty': self.volume_weight});

    def expense_calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_budget.view_project_estimate_line_cbm_calc').id

        return {
            'name': ('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.cost.estimate.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }


    def open_batch(self):
        action_ctx = dict(self.env.context)
        action_ctx['default_budget_id'] = self.approval_budget_id.id
        view_id = self.env.ref('ideatime_budget.view_budget_partB_batch').id
        return {
            'name': 'Batch Information',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.cost.estimate.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx,
        }

    def save(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('particular_ids')
    def particular_ids_onchange(self):
        if self.particular_ids:
            self.name = self.particular_ids.name

