//===========================================
// Full Screen Mode
//===========================================

odoo.define('sh_entmate_theme.full_screen_systray', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var SystrayMenu = require('web.SystrayMenu');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;


    var FullScreenTemplate = Widget.extend({
        template: "FullScreenTemplate",
        events: {
            'click .expand_img': '_click_expand_button',
            'click .compress_img': '_click_compress_button',
        },
        init: function () {
            this._super.apply(this, arguments);
            var self = this;
        },

        _click_expand_button: function (ev) {
            ev.preventDefault();
            var self = this;
            $('.expand_img').css("display", "none");
            $('.compress_img').css("display", "block");
            var elem = document.querySelector('body');
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.mozRequestFullScreen) { /* Firefox */
                elem.mozRequestFullScreen();
            } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) { /* IE/Edge */
                elem.msRequestFullscreen();
            }
        },
        _click_compress_button: function (ev) {
            ev.preventDefault();
            var self = this;
            $('.compress_img').css("display", "none");
            $('.expand_img').css("display", "block");

            $('.expand_img').css("position", "relative");
            $('.expand_img').css("top", "0%");
            var elem = document.querySelector('body');
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) { /* Firefox */
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { /* IE/Edge */
                document.msExitFullscreen();
            }
        },

    });

    FullScreenTemplate.prototype.sequence = 2;
    session.user_has_group('sh_entmate_theme.group_full_screen_mode').then(function (has_group) {
        if (has_group) {
            SystrayMenu.Items.push(FullScreenTemplate);
        }
    });


    return {
        FullScreenTemplate: FullScreenTemplate,
    };
});
//===========================================
//toggle switch if quick menu already exists
//===========================================

// odoo.define('sh_web_quick_menu.quick_menu_already', function (require) {
//     "use strict";

//     var core = require('web.core');
//     var Dialog = require('web.Dialog');
//     var Widget = require('web.Widget');
//     var rpc = require('web.rpc');
//     var SystrayMenu = require('web.SystrayMenu');

//     var _t = core._t;
//     var QWeb = core.qweb;

// });



//===========================================
//Quick Menu (main on off switch)
//===========================================

// odoo.define('sh_web_quick_menu.quick_menu', function (require) {
//     "use strict";

//     var core = require('web.core');
//     var Dialog = require('web.Dialog');
//     var Widget = require('web.Widget');
//     var rpc = require('web.rpc');
//     var SystrayMenu = require('web.SystrayMenu');
//     var session = require('web.session');
//     var _t = core._t;
//     var QWeb = core.qweb;


//     var quick_menu = Widget.extend({
//         template: "quick.menu",
//         events: {
//             click: "on_click",

//         },
//         init: function () {
//             this._super.apply(this, arguments);

//         },

//         getUrlVars: function () {
//             var vars = [], hash;
//             var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
//             for (var i = 0; i < hashes.length; i++) {
//                 hash = hashes[i].split('=');
//                 vars.push(hash[0]);
//                 vars[hash[0]] = hash[1];
//             }
//             return vars;
//         },


//         start: function () {
//             return this._super();
//         },
//         getMenuRecord: function () {
//             var action_id = $.bbq.getState().action;
//             var parent_menu_id = this.getUrlVars()["menu_id"];

//             return rpc.query({
//                 model: 'sh.wqm.quick.menu',
//                 method: 'set_quick_menu',
//                 args: ['', action_id, parent_menu_id]
//             });
//         },
//         on_click: function (ev) {
//             ev.preventDefault();
//             var self = this;
//             this.getMenuRecord().then(function (rec) {
//                 if (rec.is_set_quick_menu) {
//                     self.$el.find('> a').addClass('active');
//                 } else {
//                     self.$el.find('> a').removeClass('active');
//                 }
//             });
//             location.reload(true);

//         }
//     });

//     quick_menu.prototype.sequence = 3;
//     session.user_has_group('sh_entmate_theme.group_quick_menu_mode').then(function (has_group) {
//         if (has_group) {
//             SystrayMenu.Items.push(quick_menu);
//         }
//     });


//     return {
//         quick_menu: quick_menu,
//     };
// });




// ===========================================
//	Quick Menu List
// ===========================================

// odoo.define('sh_web_quick_menu.quick_menulist', function (require) {
//     "use strict";

//     var core = require('web.core');
//     var Dialog = require('web.Dialog');
//     var Widget = require('web.Widget');
//     var rpc = require('web.rpc');
//     var SystrayMenu = require('web.SystrayMenu');
//     var _t = core._t;
//     var QWeb = core.qweb;
//     var session = require('web.session');
//     var quick_menulist = Widget.extend({
//         template: "quick.menulist",

//         events: {
//             'click li.sh_wqm_remove_quick_menu_cls i': 'remove_quick_menu',
//         },

//         remove_quick_menu: function (e) {
//             e.stopPropagation();
//             var self = this;
//             var id = parseInt($(e.currentTarget).data('id'));
//             if (id !== NaN) {
//                 rpc.query({
//                     model: 'sh.wqm.quick.menu',
//                     method: 'remove_quick_menu_data',
//                     args: ['', id]
//                 }).then(function (res) {
//                     if (res.id) {
//                         if ($.bbq.getState(true).action == res.action_id) {
//                             self.$el.parents().find('.o_user_bookmark_menu > a').removeClass('active');
//                         }

//                         var base_url = window.location.origin;
//                         window.location = base_url + "/web";

//                     }
//                 });
//             }
//             return false;
//         },

//         init: function () {
//             this._super.apply(this, arguments);

//         },
//         start: function () {
//             var self = this;
//             var quick_menus_var = rpc.query({
//                 model: 'sh.wqm.quick.menu',
//                 method: 'get_quick_menu_data',
//                 args: ['', ['name', 'action_id', 'parent_menu_id']],
//             })
//                 .then(function (menus) {

//                     if (menus.length > 0) {
//                         self.$el.find('.sh_wqm_quick_menu_submenu_list_cls').html(QWeb.render("quick.menulist.actions", { 'quick_menulist_actions': menus }));

//                     } else {
//                         self.$el.find('.sh_wqm_quick_menu_submenu_list_cls').html("<span class='no_quick_menu'>No Bookmark !</span>")
//                     }

//                 });
//             return this._super();
//         },

//     });
//     quick_menulist.prototype.sequence = 4;
//     session.user_has_group('sh_entmate_theme.group_quick_menu_mode').then(function (has_group) {
//         if (has_group) {
//             SystrayMenu.Items.push(quick_menulist);
//         }
//     });



//     return {
//         quick_menulist: quick_menulist,
//     };
// });

