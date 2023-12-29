from odoo import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                                 lazy=lazy)
        stock = self.env['stock.quant']
        for line in res:
            if '__domain' in line:
                stock = self.search(line['__domain'])
            if 'product_uom_id' in fields:
                for rec in stock:
                    line['product_uom_id'] = rec.product_uom_id.name

        return res
