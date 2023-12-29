# -*- coding: utf-8 -*-
# from odoo import http


# class IdeatimeBudgedProjectConfigurator(http.Controller):
#     @http.route('/ideatime_budget_project_configurator/ideatime_budget_project_configurator', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ideatime_budget_project_configurator/ideatime_budget_project_configurator/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ideatime_budget_project_configurator.listing', {
#             'root': '/ideatime_budget_project_configurator/ideatime_budget_project_configurator',
#             'objects': http.request.env['ideatime_budget_project_configurator.ideatime_budget_project_configurator'].search([]),
#         })

#     @http.route('/ideatime_budget_project_configurator/ideatime_budget_project_configurator/objects/<model("ideatime_budget_project_configurator.ideatime_budget_project_configurator"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ideatime_budget_project_configurator.object', {
#             'object': obj
#         })
