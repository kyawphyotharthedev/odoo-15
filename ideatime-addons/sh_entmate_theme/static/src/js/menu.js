odoo.define('sh_entmate_theme.menu', function (require) {
    "use strict";


    var core = require('web.core');
    // var AppsMenu = require("web.AppsMenu");
    var config = require("web.config");
    // var Menu = require("web.Menu");
    var FormRenderer = require('web.FormRenderer');
    var BasicRenderer = require('web.BasicRenderer');
    var AbstractController = require("web.AbstractController");
    var QWeb = core.qweb;
    var user = require('web.session');
    var rpc = require("web.rpc");

    // var Profile = require("web.Menu");

    // var FormController = require('web.FormController');

    // FormController.include({
    //     _onContentClicked(ev) {
    //         if (this.mode === 'readonly' && user.sh_enable_one_click) {
    //             this._setMode('edit');
    //         }
    //     },

    // })
    AbstractController.include({
        start: async function () {
            var prom = this._super.apply(this, arguments);
            if (localStorage.getItem("is_full_width") == 't') {
                this.$el.find('.o_content').addClass("sh_full_content")
            } else {
                this.$el.find('.o_content').removeClass("sh_full_content")
            }
            return prom;
        },
    });
    const BaseSettingRenderer = require('base.settings').Renderer;

    BaseSettingRenderer.include({


        start: function () {
            var prom = this._super.apply(this, arguments);
            if (config.device.isMobile) {
                core.bus.on("DOM_updated", this, function () {
                    this._moveToTab(this.currentIndex || this._currentAppIndex());
                });
            }
            return prom;
        },

        _activateSettingMobileTab: function (currentTab) {
            var self = this;
            var moveTo = currentTab;
            var next = moveTo + 1;
            var previous = moveTo - 1;

            this.$(".settings .app_settings_block").removeClass("previous next current before after");
            this.$(".settings_tab .tab").removeClass("previous next current before after");
            _.each(this.modules, function (module, index) {
                var tab = self.$(".tab[data-key='" + module.key + "']");
                var view = module.settingView;

                if (index === previous) {
                    tab.addClass("previous");
                    tab.css("margin-left", "0px");
                    view.addClass("previous");
                } else if (index === next) {
                    tab.addClass("next");
                    tab.css("margin-left", "-" + tab.outerWidth() + "px");
                    view.addClass("next");
                } else if (index < moveTo) {
                    tab.addClass("before");
                    tab.css("margin-left", "-" + tab.outerWidth() + "px");
                    view.addClass("before");
                } else if (index === moveTo) {
                    var marginLeft = tab.outerWidth() / 2;
                    tab.css("margin-left", "-" + marginLeft + "px");
                    tab.addClass("current");
                    view.addClass("current");
                } else if (index > moveTo) {
                    tab.addClass("after");
                    tab.css("margin-left", "0");
                    view.addClass("after");
                }
            });
        },

        _moveToTab: function (index) {
            this.currentIndex = !index || index === -1 ? 0 : (index === this.modules.length ? index - 1 : index);
            if (this.currentIndex !== -1) {
                if (this.activeView) {
                    this.activeView.addClass("o_hidden");
                }
                if (this.activeTab) {
                    this.activeTab.removeClass("selected");
                }
                var view = this.modules[this.currentIndex].settingView;
                var tab = this.$(".tab[data-key='" + this.modules[this.currentIndex].key + "']");
                view.removeClass("o_hidden");
                this.activeView = view;
                this.activeTab = tab;
                if (config.device.isMobile) {
                    this._activateSettingMobileTab(this.currentIndex);
                } else {
                    tab.addClass("selected");
                }

            }
        },

    });


    // Responsive view "action" buttons
    FormRenderer.include({
        events: _.extend({}, BasicRenderer.prototype.events, {
            'click .full_form_toggle': '_onClickFullWidthForm',
        }),

        /**
         * In mobiles, put all statusbar buttons in a dropdown.
         *
         * @override
         */
        _renderHeaderButtons: function () {
            var $buttons = this._super.apply(this, arguments);
            if (
                !config.device.isMobile ||
                !$buttons.is(":has(>:not(.o_invisible_modifier))")
            ) {
                return $buttons;
            }

            // $buttons must be appended by JS because all events are bound
            $buttons.addClass("dropdown-menu");
            var $dropdown = $(core.qweb.render(
                'sh_entmate_theme.MenuStatusbarButtons'
            ));
            $buttons.addClass("dropdown-menu").appendTo($dropdown);
            return $dropdown;
        },
        _renderTagSheet: function (node) {
            this.has_sheet = true;
            if (user.sh_enable_full_width_form) {
                if (localStorage.getItem("is_full_width") == 't') {
                    var $sheet = $('<div>', { class: 'clearfix position-relative o_form_sheet sh_full_form' });
                    $sheet.append('<div class="sh_full_screen_icon_div"><span class="full_form_toggle"><svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 469.68 147.37"><title>exit full screen - new</title><path d="M39,267H191l-37,37s-7,8,2,17c0,0,5,8,18,3l69-65s6-6,0-15l-60-64s-10-5-19,2c0,0-10,8-5,20l33,35L40,238s-11,1-13,14C27,252,26,267,39,267Z" transform="translate(-26.98 -178.27)"/><path d="M484.65,236.91h-152l37-37s7-8-2-17c0,0-5-8-18-3l-69,65s-6,6,0,15l60,64s10,5,19-2c0,0,10-8,5-20l-33-35,152-1s11-1,13-14C496.65,251.91,497.65,236.91,484.65,236.91Z" transform="translate(-26.98 -178.27)"/></svg></span></div>')
                    $sheet.append(node.children.map(this._renderNode.bind(this)));
                    //  $(ev.currentTarget).parents().find('.o_content').addClass("sh_full_content")
                    return $sheet;
                } else {
                    var $sheet = $('<div>', { class: 'clearfix position-relative o_form_sheet' });
                    $sheet.append('<div class="sh_full_screen_icon_div"><span class="full_form_toggle"><svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 469.68 147.37"><title>full screen - new</title><path d="M233.65,236.91h-152l37-37s7-8-2-17c0,0-5-8-18-3l-69,65s-6,6,0,15l60,64s10,5,19-2c0,0,10-8,5-20l-33-35,152-1s11-1,13-14C245.65,251.91,246.65,236.91,233.65,236.91Z" transform="translate(-26.98 -178.27)"/><path d="M290,267H442l-37,37s-7,8,2,17c0,0,5,8,18,3l69-65s6-6,0-15l-60-64s-10-5-19,2c0,0-10,8-5,20l33,35-152,1s-11,1-13,14C278,252,277,267,290,267Z" transform="translate(-26.98 -178.27)"/></svg></span></div>')
                    $sheet.append(node.children.map(this._renderNode.bind(this)));
                    return $sheet;
                }

            } else {
                var $sheet = $('<div>', { class: 'clearfix position-relative o_form_sheet' });
                $sheet.append(node.children.map(this._renderNode.bind(this)));
                return $sheet;
            }

        },
        _onClickFullWidthForm: function (ev) {
            if (localStorage.getItem("is_full_width") == 't') {
                localStorage.setItem("is_full_width", "f");
                $(ev.currentTarget).parents().find('.o_form_sheet').removeClass("sh_full_form")
                $(ev.currentTarget).parents().find('.o_content').removeClass("sh_full_content")
                $(ev.currentTarget).parents().find('.full_form_toggle').replaceWith('<span class="full_form_toggle"><svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 469.68 147.37"><title>full screen - new</title><path d="M233.65,236.91h-152l37-37s7-8-2-17c0,0-5-8-18-3l-69,65s-6,6,0,15l60,64s10,5,19-2c0,0,10-8,5-20l-33-35,152-1s11-1,13-14C245.65,251.91,246.65,236.91,233.65,236.91Z" transform="translate(-26.98 -178.27)"/><path d="M290,267H442l-37,37s-7,8,2,17c0,0,5,8,18,3l69-65s6-6,0-15l-60-64s-10-5-19,2c0,0-10,8-5,20l33,35-152,1s-11,1-13,14C278,252,277,267,290,267Z" transform="translate(-26.98 -178.27)"/></svg></span>')

            } else {
                localStorage.setItem("is_full_width", "t");
                $(ev.currentTarget).parents().find('.o_form_sheet').addClass("sh_full_form")
                $(ev.currentTarget).parents().find('.o_content').addClass("sh_full_content")
                $(ev.currentTarget).parents().find('.full_form_toggle').replaceWith('<span class="full_form_toggle"><svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 469.68 147.37"><title>exit full screen - new</title><path d="M39,267H191l-37,37s-7,8,2,17c0,0,5,8,18,3l69-65s6-6,0-15l-60-64s-10-5-19,2c0,0-10,8-5,20l33,35L40,238s-11,1-13,14C27,252,26,267,39,267Z" transform="translate(-26.98 -178.27)"/><path d="M484.65,236.91h-152l37-37s7-8-2-17c0,0-5-8-18-3l-69,65s-6,6,0,15l60,64s10,5,19-2c0,0,10-8,5-20l-33-35,152-1s11-1,13-14C496.65,251.91,497.65,236.91,484.65,236.91Z" transform="translate(-26.98 -178.27)"/></svg></span>')

            }


        },

    });


    var RelationalFields = require('web.relational_fields');

    RelationalFields.FieldStatus.include({

        /**
         * Fold all on mobiles.
         *
         * @override
         */
        _setState: function () {
            this._super.apply(this, arguments);
            if (config.device.isMobile) {
                _.map(this.status_information, function (value) {
                    value.fold = true;
                });
            }
        },
    });




    // Menu.include({
    //     events: _.extend({
    //         // Clicking a hamburger menu item should close the hamburger
    //         //  "click .o_menu_sections [role=menuitem]": "_hideMobileSubmenus",
    //         // Opening any dropdown in the navbar should hide the hamburger
    //         //	  "show.bs.dropdown  .o_menu_systray":"_showo_menu_systray",

    //         "show.bs.dropdown  .o_menu_apps": "_hideMobileSubmenus",
    //         "hide.bs.dropdown  .o_menu_apps": "_hideappMenu",
    //         "click #app_toggle": "click_app_toggle",


    //     }, Menu.prototype.events),

    //     //    _showo_menu_systray:function(){
    //     //    	alert("6")
    //     //    	if()
    //     //    },
    //     click_app_toggle: function () {
    //         if ($(".sh_entmate_theme_appmenu_div").hasClass("show")) {
    //             $("body").removeClass("sh_sidebar_background_enterprise");
    //             $(".sh_search_container").css("display", "none");

    //             $(".sh_entmate_theme_appmenu_div").removeClass("show")
    //             $(".o_action_manager").removeClass("d-none");
    //             $(".o_menu_brand").css("display", "block");
    //             $(".full").removeClass("sidebar_arrow");
    //             $(".o_menu_sections").css("display", "block");
    //         } else {
    //             $(".sh_entmate_theme_appmenu_div").addClass("show")
    //             $("body").addClass("sh_sidebar_background_enterprise");
    //             $(".sh_entmate_theme_appmenu_div").css("opacity", "1");
    //             //$(".sh_search_container").css("display","block");
    //             $(".o_action_manager").addClass("d-none");
    //             $(".full").addClass("sidebar_arrow");
    //             $(".o_menu_brand").css("display", "none");
    //             $(".o_menu_sections").css("display", "none");
    //         }

    //     },
    //     start: function () {
    //         this.$menu_toggle = this.$(".sh-mobile-toggle");
    //         return this._super.apply(this, arguments);
    //     },

    //     _hideappMenu: function (ev) {

    //     },
    //     _hideMobileSubmenus: function () {

    //         if (
    //             this.$menu_toggle.is(":visible") &&
    //             this.$section_placeholder.is(":visible")
    //         ) {
    //             this.$section_placeholder.collapse("hide");
    //         }
    //     },


    //     _updateMenuBrand: function () {
    //         if (!config.device.isMobile) {
    //             return this._super.apply(this, arguments);
    //         }
    //     },
    // });
    if (!config.device.isMobile) {
        return;
    }
    // Profile.include({

    //     events: _.extend({
    //         //  "click .o_menu_sections [role=menuitem]": "_hideMobileSubmenus",
    //         //	  "show.bs.dropdown  .o_menu_systray":"_showo_menu_systray",

    //         'click .sh-mobile-toggle': '_onOpenProfileSection',
    //         'click #close_submenu': '_closeSubMenuSection'

    //     }, Menu.prototype.events),


    //     menusTemplate: 'Submenu.sections',

    //     start: function () {
    //         return this._super.apply(this, arguments).then(this._renderProfileSection.bind(this));
    //     },

    //     _closeSubMenuSection: function () {
    //         $(".sh_profile_menu").addClass("o_hidden");
    //     },

    //     _renderProfileSection: function () {
    //         this.$ProfileSection = $(QWeb.render('ProfileSection', {}));
    //         this.$ProfileSection.addClass("o_hidden");

    //         this.$section_placeholder.appendTo(this.$ProfileSection.find('.sh_profile_menu_app'));
    //         this.$ProfileSection.on('click', '.sh_profile_menu_section', this._onProfileSectionSectionClick.bind(this));
    //         this.$ProfileSection.on('click', '#close_submenu', this._closeSubMenuSection.bind(this));
    //         $('.o_web_client').append(this.$ProfileSection);
    //     },

    //     _onProfileSectionSectionClick: function (ev) {
    //         ev.preventDefault();
    //         ev.stopPropagation();
    //         $(ev.currentTarget).toggleClass('show');

    //         $(ev.currentTarget).find('> a #sub_menu').toggleClass('fa-chevron-down fa-chevron-right');
    //     },

    //     _onOpenProfileSection: function (ev) {
    //         ev.preventDefault();
    //         var app = _.findWhere(this.menu_data.children, { id: this.current_primary_menu });

    //         var toggle_boolean = true;

    //         if (!!(app && app.children.length)) {
    //             toggle_boolean = true
    //         } else {
    //             toggle_boolean = false
    //         }


    //         this.$ProfileSection.find('#mobile_body').toggleClass('sh_profile_menu_dark', toggle_boolean);
    //         this.$ProfileSection.find('.sh_profile_menu_app').toggleClass('o_hidden', !toggle_boolean);
    //         // hide section
    //         // if(toggle_boolean == true){
    //         $(".sh_profile_menu").removeClass('o_hidden');
    //         //  }

    //     },

    //     _on_secondary_menu_click: function () {
    //         this._super.apply(this, arguments);
    //         $(".sh_profile_menu").addClass("o_hidden");
    //     },



    // });

});
