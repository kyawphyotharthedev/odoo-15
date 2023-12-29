# -*- coding: utf-8 -*-
# from odoo import http


# class IdeatimeExpense(http.Controller):
#     @http.route('/ideatime_expense/ideatime_expense', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ideatime_expense/ideatime_expense/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ideatime_expense.listing', {
#             'root': '/ideatime_expense/ideatime_expense',
#             'objects': http.request.env['ideatime_expense.ideatime_expense'].search([]),
#         })

#     @http.route('/ideatime_expense/ideatime_expense/objects/<model("ideatime_expense.ideatime_expense"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ideatime_expense.object', {
#             'object': obj
#         })
