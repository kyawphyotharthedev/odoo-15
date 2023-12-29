# -*- coding: utf-8 -*-
# from odoo import http


# class IdeatimeUom(http.Controller):
#     @http.route('/ideatime_uom/ideatime_uom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ideatime_uom/ideatime_uom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ideatime_uom.listing', {
#             'root': '/ideatime_uom/ideatime_uom',
#             'objects': http.request.env['ideatime_uom.ideatime_uom'].search([]),
#         })

#     @http.route('/ideatime_uom/ideatime_uom/objects/<model("ideatime_uom.ideatime_uom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ideatime_uom.object', {
#             'object': obj
#         })
