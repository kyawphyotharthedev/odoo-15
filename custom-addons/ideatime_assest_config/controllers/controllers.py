# -*- coding: utf-8 -*-
# from odoo import http


# class IdeatimeAssestConfig(http.Controller):
#     @http.route('/ideatime_assest_config/ideatime_assest_config', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ideatime_assest_config/ideatime_assest_config/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ideatime_assest_config.listing', {
#             'root': '/ideatime_assest_config/ideatime_assest_config',
#             'objects': http.request.env['ideatime_assest_config.ideatime_assest_config'].search([]),
#         })

#     @http.route('/ideatime_assest_config/ideatime_assest_config/objects/<model("ideatime_assest_config.ideatime_assest_config"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ideatime_assest_config.object', {
#             'object': obj
#         })
