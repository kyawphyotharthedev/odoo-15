import math
from operator import itemgetter

from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, groupby
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    agreement_period_id = fields.Many2one('agreement.period.template', string="Agreegment Period Template")
    agreement_period_note = fields.Text()
    commencement_date = fields.Date()
    commencement_start_date = fields.Date()
    commencement_end_date = fields.Date()
    currency_template_id = fields.Many2one('currency.template')
    currency_note = fields.Text()
    price_fee_id = fields.Many2one('price.fee.template')
    price_fee_note = fields.Text()
    taxation_template_id = fields.Many2one('taxation.template')
    taxation_note = fields.Text()
    payment_template_id = fields.Many2one('payment.template')
    payment_note = fields.Text()
    acceptance_template_id = fields.Many2one('acceptance.template')
    acceptance_note = fields.Text()
    obligation_template_id = fields.Many2one('obligation.template')
    obligation_note = fields.Text()
    contract_template_id = fields.Many2one('contract.template')
    contract_note = fields.Text()
    termination_template_id = fields.Many2one('termination.template')
    termination_note = fields.Text()
    arbitration_template_id = fields.Many2one('arbitration.template')
    arbitration_note = fields.Text()
    project_id = fields.Many2one('project.project', string='Project', required="True")
    project_site_id = fields.Char(related="project_id.project_site")
    project_name = fields.Char(compute="_compute_project_name")
    project_client_id = fields.Char(related="project_id.partner_id.name")

    budget_id = fields.Many2one('budget.approval', required="True")
    batch_id = fields.Many2one('approval.budget.line', domain="[('approval_budget_id', '=',budget_id)]",
                               required="True")

    @api.onchange('batch_id')
    def button_update(self):
        for record in self:
            order_lines = []
            procurement_lines = record.batch_id.batch_budget_line.filtered(
                lambda line: line.usage_type == 'proc'
            )

            procurement_lines = sorted(procurement_lines,
                                       key=lambda line: (line.product_id, line.batch_id, line.budget_id))

            for (product, batch, budget), lines in groupby(procurement_lines,
                                                           key=itemgetter('product_id', 'batch_id', 'budget_id')):

                total_qty = sum(line.product_uom_qty for line in lines)
                total_amount = sum(line.product_uom_qty * line.unit_price for line in lines)

                order_line = {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom': math.ceil(lines[0].unit.id),
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_qty': total_qty,
                    'price_unit': int(total_amount),
                }

                order_lines.append((0, 0, order_line))

            vals = {'order_line': order_lines}
            record.order_line = None
            record.write(vals)

    @api.onchange('project_id')
    def _compute_project_name(self):
        for record in self:

            service_project_name = []
            if record.project_client_id:
                service_project_name.append(record.project_client_id)

            if record.project_id.cate_sector_id:
                service_project_name.append(str(record.project_id.cate_sector_id.name))
            if record.project_id.cate_line_id:
                service_project_name.append(str(record.project_id.cate_line_id.name))

            if record.project_id.manual_project_name:
                service_project_name.append(str(record.project_id.manual_project_name))

            record.project_name = " ".join(str(x) for x in service_project_name)

    @api.onchange('agreement_period_id')
    def onchange_agreement_period_template_id(self):
        if not self.agreement_period_id:
            return
        self.agreement_period_note = self.agreement_period_id.descrption

    @api.onchange('currency_template_id')
    def onchange_currency_template_id(self):
        if not self.currency_template_id:
            return
        self.currency_note = self.currency_template_id.descrption

    @api.onchange('price_fee_id')
    def onchange_price_fee_template_id(self):
        if not self.price_fee_id:
            return
        self.price_fee_note = self.price_fee_id.descrption

    @api.onchange('taxation_template_id')
    def onchange_taxation_template_id(self):
        if not self.taxation_template_id:
            return
        self.taxation_note = self.taxation_template_id.descrption

    @api.onchange('payment_template_id')
    def onchange_payment_template_id(self):
        if not self.payment_template_id:
            return
        self.payment_note = self.payment_template_id.descrption

    @api.onchange('acceptance_template_id')
    def onchange_acceptance_template_id(self):
        if not self.acceptance_template_id:
            return
        self.acceptance_note = self.acceptance_template_id.descrption

    @api.onchange('obligation_template_id')
    def onchange_obligation_template_id(self):
        if not self.obligation_template_id:
            return
        self.obligation_note = self.obligation_template_id.descrption

    @api.onchange('contract_template_id')
    def onchange_contract_template_id(self):
        if not self.contract_template_id:
            return
        self.contract_note = self.contract_template_id.descrption

    @api.onchange('termination_template_id')
    def onchange_termination_template_id(self):
        if not self.termination_template_id:
            return
        self.termination_note = self.termination_template_id.descrption

    @api.onchange('arbitration_template_id')
    def onchange_arbitration_template_id(self):
        if not self.arbitration_template_id:
            return
        self.arbitration_note = self.arbitration_template_id.descrption

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id,
                'project_id': self.project_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'project_id': self.project_id,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'project_id': self.project_id.id
        }

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['project_id'] = self.project_id.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    remark = fields.Text(string="Remark")
    product_id = fields.Many2one('product.product', string='Product',
                                 domain=[('purchase_ok', '=', True), ('is_return_product', '=', False)],
                                 change_default=True, required=True)
    barcode = fields.Text(string='Barcode')
    product_uom_label = fields.Char()

    # fields for Calculate CBM function
    Pcs = fields.Float(string='Unit', default=1, copy=False, digits=(12, 3))
    length = fields.Float(string='Length', default=1, copy=False, digits=(12, 3))
    width = fields.Float(string='Width', default=1, copy=False, digits=(12, 3))
    height = fields.Float(string='Height', default=1, copy=False, digits=(12, 3))
    volume_weight = fields.Float(string='Result', default=1, copy=False, digits=(12, 3))

    # uom field for  Calculate CBM form
    pcs_uom = fields.Many2one('uom.uom', string='Unit UOM')
    length_uom = fields.Many2one('uom.uom', string='Length UOM')
    width_uom = fields.Many2one('uom.uom', string='Width UOM')
    height_uom = fields.Many2one('uom.uom', string='Height UOM')

    # Calculate CBM function

    def calculate_cbm(self):
        action_ctx = dict(self.env.context)
        view_id = self.env.ref('ideatime_purchase.view_purchase_order_line_cbm_calc').id

        return {
            'name': _('CBM Calculate'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.line',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx
        }

    def save(self):
        self.product_qty = self.volume_weight
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('length', 'width', 'height', 'Pcs', 'volume_weight')
    def _calc_cbm_onchange(self):
        if self.length > 0 and self.width > 0 and self.height > 0 and self.Pcs > 0:
            self.volume_weight = (self.length * self.width * self.height * self.Pcs)

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        self.barcode = self.product_id.barcode
        self.product_uom_label = self.product_id.uom_id.uom_label
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        self._compute_tax_id()

        self._suggest_quantity()
        self._onchange_quantity()

        return result

    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(
                lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_uom
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = self.product_uom._compute_quantity(diff_quantity, self.product_uom,
                                                                                 rounding_method='HALF-UP')
            res.append(template)
        return res
