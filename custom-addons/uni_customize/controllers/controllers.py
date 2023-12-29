# -*- coding: utf-8 -*-
# from odoo import http


# class UniCustomize(http.Controller):
#     @http.route('/uni_customize/uni_customize', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/uni_customize/uni_customize/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('uni_customize.listing', {
#             'root': '/uni_customize/uni_customize',
#             'objects': http.request.env['uni_customize.uni_customize'].search([]),
#         })

#     @http.route('/uni_customize/uni_customize/objects/<model("uni_customize.uni_customize"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('uni_customize.object', {
#             'object': obj
#         })
