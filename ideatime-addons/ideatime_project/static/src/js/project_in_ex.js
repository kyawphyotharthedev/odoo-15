odoo.define('ideatime_project.project_in_ex', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var framework = require('web.framework');

var QWeb = core.qweb;

var project_in_ex = AbstractAction.extend({
    hasControlPanel: true,
	events: {
        'click .o_mrp_bom_unfoldable': '_onClickUnfold',
        'click .o_mrp_bom_foldable': '_onClickFold',
        'click .o_mrp_bom_action': '_onClickAction',
    },
    init: function(parent, action) {
        this._super.apply(this, arguments);
        this.actionManager = parent;
        this.given_context = session.user_context;
        this.controller_url = action.context.url;
        if (action.context.context) {
            this.given_context = action.context.context;
        }
        this.given_context.active_id = action.context.active_id || action.params.active_id;
        this.given_context.model = action.context.active_model || false;
        this.given_context.ttype = action.context.ttype || false;
        this.given_context.auto_unfold = action.context.auto_unfold || false;
        this.given_context.lot_name = action.context.lot_name || false;
    },
    willStart: function() {
        return Promise.all([this._super.apply(this, arguments), this.get_html()]);
    },
    set_html: function() {
        var self = this;
        var def = $.when();
        if (!this.report_widget) {
            this.report_widget = new Widget(this, this.given_context);
            def = this.report_widget.appendTo(this.$el);
        }
        return def.then(function () {
            self.$el.html(self.data.data);
        });
    },
    _onClickUnfold: function (ev) {
        var redirect_function = $(ev.currentTarget).data('function');
        this[redirect_function](ev);
    },
    _onClickFold: function (ev) {
        this._removeLines($(ev.currentTarget).closest('tr'));
        $(ev.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
    },
    _onClickAction: function (ev) {
        ev.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            views: [[false, 'form']],
            target: 'current'
        });
    },
    start: async function() {
        await this._super(...arguments);
        this.set_html();
    },
    // Fetches the html and is previous report.context if any, else create it
    get_html: function() {
        var self = this;
        var args = [
            this.given_context.active_id,
        ];
        return this._rpc({
                model: 'report.ideatime_project.report_in_ex',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
            });
    },
    get_inv_line: function(ev) {
        var self = this;
        var $parent = $(ev.currentTarget).closest('tr');
        var activeID = $parent.data('res-id');
        var level = 1;
        return this._rpc({
              model: 'report.ideatime_project.report_in_ex',
              method: 'get_inv_line',
              args: [
                  activeID,
                  level
              ]
          })
          .then(function (result) {
              self.render_html(ev, $parent, result);
          });
    },
    get_exp_line: function(ev) {
        var self = this;
        var $parent = $(ev.currentTarget).closest('tr');
        var activeID = $parent.data('res-id');
        var level = 1;
        return this._rpc({
              model: 'report.ideatime_project.report_in_ex',
              method: 'get_exp_line',
              args: [
                  activeID,
                  level
              ]
          })
          .then(function (result) {
              self.render_html(ev, $parent, result);
          });
    },
    render_html: function(event, $el, result){

        $el.after(result);
        $(event.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
        this._reload_report_type();
    },
    _reload_report_type: function () {
        this.$('.o_mrp_bom_cost').toggleClass('');
    },
    _removeLines: function ($el) {
        var self = this;
        var activeID = $el.data('res-id');
        _.each(this.$('tr[parent_id='+ activeID +']'), function (parent) {
            var $parent = self.$(parent);
            var $el = self.$('tr[parent_id='+ $parent.data('res-id') +']');
            if ($el.length) {
                self._removeLines($parent);
            }
            $parent.remove();
        });
    },

});

core.action_registry.add('project_in_ex', project_in_ex);
return project_in_ex;

});
