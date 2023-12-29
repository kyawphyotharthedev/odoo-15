odoo.define('ideatime_product_configurator.ProductConfiguratorFormController', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var FormController = require('web.FormController');

var ProductConfiguratorFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        field_changed: '_onFieldChanged'
    }),
    className: 'o_product_configurator',
    /**
     * @override
     */
    init: function (){
        this._super.apply(this, arguments);
    },
    /**
     * We need to override the default click behavior for our "Add" button
     * because there is a possibility that this product has optional products.
     * If so, we need to display an extra modal to choose the options.
     *
     * @override
     */
    _onButtonClicked: function (event) {
        if (event.stopPropagation){
            event.stopPropagation();
        }
        var attrs = event.data.attrs;
        if (attrs.special === 'cancel') {
            this._super.apply(this, arguments);
        } else {
            if (!this.$el
                    .parents('.modal')
                    .find('.o_sale_product_configurator_add')
                    .hasClass('disabled')){
                this._handleAdd(this.$el);
            }
        }
    },
    /**
     * This is overridden to allow catching the "select" event on our product template select field.
     * This will not work anymore if more fields are added to the form.
     * TODO awa: Find a better way to catch that event.
     *
     * @override
     */
    _onFieldChanged: function (event) {
        this._super.apply(this, arguments);

        var self = this;
        if(event.data.changes.hasOwnProperty('product_template_id')){
            var product_id = event.data.changes.product_template_id.id;
        }


        var cost_type_id = event.data.changes.cost_type_id?.id;

         if (cost_type_id){
            this._rpc({
                route: '/ideatime_product_configurator/store_cost_type',
                params: {
                    cost_type_id : cost_type_id
                }
            }).then(function (configurator) {
                self.renderer.renderCostType(configurator);
            });

        }

        // check to prevent traceback when emptying the field
        if (!product_id) {
            return;
        }


        this.$el.parents('.modal').find('.o_sale_product_configurator_add').removeClass('disabled');

        this._rpc({
            route: '/ideatime_product_configurator/configure',
            params: {
                product_id: product_id,
                pricelist_id: this.renderer.pricelistId,
            }
        }).then(function (configurator) {
            self.renderer.renderConfigurator(configurator);
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
    * When the user adds a product that has optional products, we need to display
    * a window to allow the user to choose these extra options.
    *
    * This will also create the product if it's in "dynamic" mode
    * (see product_attribute.create_variant)
    *
    * @private
    * @param {$.Element} $modal
    */
    _handleAdd: function ($modal) {
        var self = this;
        var $modal = this.$el;
        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];

        var productId = parseInt($modal.find(productSelector.join(', ')).first().val(), 10);
        var productTemplateId = $modal.find('.product_template_id').val();
        var cost_type_id = parseInt($modal.find('.cost_type_id').val(),10);
        this.renderer.selectOrCreateProduct(
            $modal,
            productId,
            productTemplateId,
            false
        ).then(function (productId) {
            $modal.find(productSelector.join(', ')).val(productId);

            var variantValues = self
                .renderer
                .getSelectedVariantValues($modal.find('.js_product'));

            var productCustomVariantValues = self
                .renderer
                .getCustomVariantValues($modal.find('.js_product'));

            var noVariantAttributeValues = self
                .renderer
                .getNoVariantAttributeValues($modal.find('.js_product'));

            self.rootProduct = {
                product_id: productId,
                cost_type_id : cost_type_id,
                quantity: parseFloat($modal.find('input[name="add_qty"]').val() || 1),
                variant_values: variantValues,
                product_custom_attribute_values: productCustomVariantValues,
                no_variant_attribute_values: noVariantAttributeValues
            };
            self._addProducts([self.rootProduct]);
        });
    },

    /**
     * No optional products found for this product, only add the root product
     *
     * @private
     */
    _onModalOptionsEmpty: function () {
        this._addProducts([this.rootProduct]);
    },

    /**
     * Add all selected products
     *
     * @private
     */
    _onModalConfirm: function () {
        this._addProducts(this.optionalProductsModal.getSelectedProducts());
    },

    /**
     * Update product configurator form
     * when quantity is updated in the optional products window
     *
     * @private
     * @param {integer} quantity
     */
    _onOptionsUpdateQuantity: function (quantity) {
        this.$el
            .find('input[name="add_qty"]')
            .val(quantity)
            .trigger('change');
    },

    /**
    * This triggers the close action for the window and
    * adds the product as the "infos" parameter.
    * It will allow the caller (typically the SO line form) of this window
    * to handle the added products.
    *
    * @private
    * @param {Array} products the list of added products
    *   {integer} products.product_id: the id of the product
    *   {integer} products.quantity: the added quantity for this product
    *   {Array} products.product_custom_attribute_values:
    *     see product_configurator_mixin.getCustomVariantValues
    *   {Array} products.no_variant_attribute_values:
    *     see product_configurator_mixin.getNoVariantAttributeValues
    */
    _addProducts: function (products) {
        this.do_action({type: 'ir.actions.act_window_close', infos: products});
    }
});

return ProductConfiguratorFormController;

});