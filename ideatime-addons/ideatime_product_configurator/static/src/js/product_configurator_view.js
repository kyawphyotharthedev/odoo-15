odoo.define('ideatime_product_configurator.ProductConfiguratorFormView', function (require) {
"use strict";

var ProductConfiguratorFormController = require('ideatime_product_configurator.ProductConfiguratorFormController');
var ProductConfiguratorFormRenderer = require('ideatime_product_configurator.ProductConfiguratorFormRenderer');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var ProductConfiguratorFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: ProductConfiguratorFormController,
        Renderer: ProductConfiguratorFormRenderer,
    }),
});

viewRegistry.add('ideatime_product_configurator_form', ProductConfiguratorFormView);

return ProductConfiguratorFormView;

});