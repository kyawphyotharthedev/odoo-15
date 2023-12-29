# -*- coding: utf-8 -*-
# from odoo import http


# class IdeatimeProductConfig(http.Controller):
#     @http.route('/ideatime_product_config/ideatime_product_config', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ideatime_product_config/ideatime_product_config/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ideatime_product_config.listing', {
#             'root': '/ideatime_product_config/ideatime_product_config',
#             'objects': http.request.env['ideatime_product_config.ideatime_product_config'].search([]),
#         })

#     @http.route('/ideatime_product_config/ideatime_product_config/objects/<model("ideatime_product_config.ideatime_product_config"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ideatime_product_config.object', {
#             'object': obj
#         })
