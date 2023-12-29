from odoo import models, fields, api, _


class ExpenseVoucher(models.Model):
    _name = 'expense.voucher'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Expense Voucher'

    @api.depends('voucher_line_ids.price_subtotal')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            total_amt = 0.0
            for line in order.voucher_line_ids:
                total_amt += line.price_subtotal
            order.update({
                'amount_total': total_amt,
            })

    @api.model
    def get_company_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string='Name')
    # option_id = fields.Many2one('cost.option', string='Cost Option', required=True)
    project_ids = fields.Many2many('project.project', string='Project', required=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    voucher_line_ids = fields.One2many('expense.voucher.line', 'voucher_id')
    currency_id = fields.Many2one('res.currency', default=get_company_currency_id)
    valid_date = fields.Date('Date Validity', default=fields.Date.today(), readonly=True)
    date = fields.Date('Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Done'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled'),
    ], string='Status', copy=False, tracking=True, default='draft')

    @api.model
    def create(self, vals):
        search_seq = self.env['ir.sequence'].search([('code', '=', 'ExpVou')], limit=1)
        vals['name'] = search_seq.next_by_id()
        return super(ExpenseVoucher, self).create(vals)


class ExpenseVoucherLine(models.Model):
    _name = 'expense.voucher.line'
    _description = 'Expense Voucher Line'

    @api.depends('qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the Expense line.
        """
        for line in self:
            price = line.price_unit * line.qty
            line.update({
                'price_subtotal': price,
            })

    sequence = fields.Integer(string='Sequence', default=10)
    voucher_id = fields.Many2one('expense.voucher', string='Voucher')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    supplier_item_name = fields.Char('Item name(Supplier)')
    description = fields.Text('Specification/Description')
    size_service = fields.Char('Size/Service')
    qty = fields.Float('Qty')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    price_unit = fields.Float('Price')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    currency_id = fields.Many2one('res.currency', related='voucher_id.currency_id')
