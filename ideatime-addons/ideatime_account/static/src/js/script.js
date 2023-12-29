odoo.define('ideatime_account.DynamicTbMain', function (require) {
    'use strict';
    var core = require('web.core');
    var DynamicAccountReport = require('account_dynamic_reports.DynamicTbMain');
    var field_utils = require('web.field_utils');
    var QWeb = core.qweb;

    var DynamicFrMain = DynamicAccountReport.DynamicFrMain.extend({
        plot_data: function (initial_render = true) {
            var self = this;
            var node = self.$('.py-data-container');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.financial.report',
                method: 'get_report_values',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas.form;
                self.account_data = datas.report_lines;
                var formatOptions = {
                    currency_id: datas.currency,
                    noSymbol: true,
                };
                self.initial_balance = self.formatWithSign(datas.initial_balance, formatOptions, datas.initial_balance < 0 ? '-' : '');
                self.current_balance = self.formatWithSign(datas.current_balance, formatOptions, datas.current_balance < 0 ? '-' : '');
                self.ending_balance = self.formatWithSign(datas.ending_balance, formatOptions, datas.ending_balance < 0 ? '-' : '');
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.balance_cmp = self.formatWithSign(k.balance_cmp, formatOptions, k.balance < 0 ? '-' : '');
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionFr', {
                        filter_data: self.filter_data,
                    }));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_from_cmp').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to_cmp').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                    self.$el.find('.analytic-tag-multiple').select2({
                        placeholder: 'Analytic Tags...',
                    });
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Select Analytic...',
                    });
                    self.$el.find('.project-multiple').select2({
                        placeholder: 'Select Project...',
                    });
                    self.$el.find('.project-type-multiple').select2({
                        placeholder: 'Select Project Type...',
                    });
                    //Add Project Type Filter Onchange Event
                    self.$el.find(".project-type-multiple").on("change", function (e) {
                        //Remove currently selected projects
                        $('.project-multiple').select2('val', []);
                        //Get selected project types
                        let project_type_ids = $(this).val();
                        if (project_type_ids.length > 0) {
                            datas['form']['project_list'].map(function(project){
                                let intersect_project_type_ids = project_type_ids.filter(function(project_type_id){
                                    return project[2].includes(parseInt(project_type_id));
                                });
                                if(intersect_project_type_ids.length > 0){
                                    $(".project-multiple").find("option[value='" + project[0] + "']").removeAttr('disabled');
                                }else{
                                    $(".project-multiple").find("option[value='" + project[0] + "']").attr("disabled", true);
                                }
                            });
                        }else{
                            $(".project-multiple").find("option").removeAttr('disabled');
                        }
                    });
                    self.$el.find(".project-type-multiple").trigger('change.select2');


                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    });
                }
                self.$('.py-data-container').html(QWeb.render('DataSectionFr', {
                    account_data: self.account_data,
                    filter_data: self.filter_data,
                }));
                if (parseFloat(datas.initial_balance) > 0 || parseFloat(datas.current_balance) > 0 || parseFloat(datas.ending_balance) > 0) {
                    $(".py-data-container").append(QWeb.render('SummarySectionFr', {
                        initial_balance: self.initial_balance,
                        current_balance: self.current_balance,
                        ending_balance: self.ending_balance
                    }));
                }
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range: false, enable_filter: false, debit_credit: false};
            if ($(".date_filter-multiple").select2('data').length === 1) {
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
                output.date_to = false;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
                output.date_from = false;
            }
            if ($("#date_from").val() && $("#date_to").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
            }
            if ($("#date_from_cmp").val()) {
                var dateObject = $("#date_from_cmp").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from_cmp = dateString;
                output.enable_filter = true;
            }
            if ($("#date_to_cmp").val()) {
                var dateObject = $("#date_to_cmp").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to_cmp = dateString;
                output.enable_filter = true;
            }
            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids

            var project_ids = [];
            var project_list = $(".project-multiple").select2('data')
            for (var i = 0; i < project_list.length; i++) {
                project_ids.push(parseInt(project_list[i].id))
            }
            output.project_ids = project_ids

            var proj_type_ids = [];
            var project_type_list = $(".project-type-multiple").select2('data')
            for (var i = 0; i < project_type_list.length; i++) {
                proj_type_ids.push(parseInt(project_type_list[i].id))
            }
            output.proj_type_ids = proj_type_ids

            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i = 0; i < analytic_list.length; i++) {
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            output.analytic_ids = analytic_ids
            var analytic_tag_ids = [];
            var analytic_tag_list = $(".analytic-tag-multiple").select2('data')
            for (var i = 0; i < analytic_tag_list.length; i++) {
                analytic_tag_ids.push(parseInt(analytic_tag_list[i].id))
            }
            output.analytic_tag_ids = analytic_tag_ids
            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'debit_credit') {
                    output.debit_credit = true;
                }
            }
            self._rpc({
                model: 'ins.financial.report',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },

    });

    var DynamicGlMain = DynamicAccountReport.DynamicGlMain.extend({
        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.general.ledger',
                method: 'get_report_datas',
                args: [
                    [self.wizard_id]
                ],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.account_data = datas[1]
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.ldate = field_utils.format.date(field_utils.parse.date(k.ldate, {}, {
                        isUTC: true
                    }));
                    _.each(k.lines, function (ks, vs) {
                        ks.debit = self.formatWithSign(ks.debit, formatOptions, ks.debit < 0 ? '-' : '');
                        ks.credit = self.formatWithSign(ks.credit, formatOptions, ks.credit < 0 ? '-' : '');
                        ks.balance = self.formatWithSign(ks.balance, formatOptions, ks.balance < 0 ? '-' : '');
                        ks.ldate = field_utils.format.date(field_utils.parse.date(ks.ldate, {}, {
                            isUTC: true
                        }));
                    });
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSection', {
                        filter_data: datas[0],
                    }));
                    self.$el.find('#date_from').datepicker({
                        dateFormat: 'dd-mm-yy'
                    });
                    self.$el.find('#date_to').datepicker({
                        dateFormat: 'dd-mm-yy'
                    });
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val(['include_details', 'initial_balance']).trigger('change');
                    self.$el.find('.account-multiple').select2({
                        placeholder: 'Select Account...',
                    });
                    self.$el.find('.account-tag-multiple').select2({
                        placeholder: 'Account Tags...',
                    });
                    self.$el.find('.analytic-tag-multiple').select2({
                        placeholder: 'Analytic Tags...',
                    });
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Select Analytic...',
                    });
                    self.$el.find('.project-multiple').select2({
                        placeholder: 'Select Project...',
                    });
                    self.$el.find('.project-type-multiple').select2({
                        placeholder: 'Select Project Type...',
                    });
                    //Add Project Type Filter Onchange Event
                    self.$el.find(".project-type-multiple").on("change", function (e) {
                        //Remove currently selected projects
                        $('.project-multiple').select2('val', []);
                        //Get selected project types
                        let project_type_ids = $(this).val();
                        if (project_type_ids.length > 0) {
                            datas[0]['projects_list'].map(function(project){
                                let intersect_project_type_ids = project_type_ids.filter(function(project_type_id){
                                    return project[2].includes(parseInt(project_type_id));
                                });
                                if(intersect_project_type_ids.length > 0){
                                    $(".project-multiple").find("option[value='" + project[0] + "']").removeAttr('disabled');
                                }else{
                                    $(".project-multiple").find("option[value='" + project[0] + "']").attr("disabled", true);
                                }
                            });
                        }else{
                            $(".project-multiple").find("option").removeAttr('disabled');
                        }
                    });
                    self.$el.find(".project-type-multiple").trigger('change.select2');


                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                }
                self.$('.py-data-container-orig').html(QWeb.render('DataSection', {
                    account_data: datas[1]
                }));
                self.loader_enable_ui();
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {
                date_range: false
            };
            output.display_accounts = 'balance_not_zero';
            output.initial_balance = false;
            output.include_details = false;
            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids
            var account_ids = [];
            var account_list = $(".account-multiple").select2('data')
            for (var i = 0; i < account_list.length; i++) {
                account_ids.push(parseInt(account_list[i].id))
            }
            output.account_ids = account_ids
            var account_tag_ids = [];
            var account_tag_list = $(".account-tag-multiple").select2('data')
            for (var i = 0; i < account_tag_list.length; i++) {
                account_tag_ids.push(parseInt(account_tag_list[i].id))
            }
            output.account_tag_ids = account_tag_ids
            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i = 0; i < analytic_list.length; i++) {
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            output.analytic_ids = analytic_ids
            var analytic_tag_ids = [];
            var analytic_tag_list = $(".analytic-tag-multiple").select2('data')
            for (var i = 0; i < analytic_tag_list.length; i++) {
                analytic_tag_ids.push(parseInt(analytic_tag_list[i].id))
            }
            output.analytic_tag_ids = analytic_tag_ids
            if ($(".date_filter-multiple").select2('data').length === 1) {
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }

            var project_ids = [];
            var project_list = $(".project-multiple").select2('data')
            for (var i = 0; i < project_list.length; i++) {
                project_ids.push(parseInt(project_list[i].id))
            }
            output.project_ids = project_ids

            var proj_type_ids = [];
            var project_types_list = $(".project-type-multiple").select2('data')
            for (var i = 0; i < project_types_list.length; i++) {
                proj_type_ids.push(parseInt(project_types_list[i].id))
            }
            output.proj_type_ids = proj_type_ids

            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'initial_balance') {
                    output.initial_balance = true;
                }
                if (options_list[i].id === 'bal_not_zero') {
                    output.display_accounts = 'balance_not_zero';
                }
                if (options_list[i].id === 'include_details') {
                    output.include_details = true;
                }
            }
            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
            }
            self._rpc({
                model: 'ins.general.ledger',
                method: 'write',
                args: [
                    [self.wizard_id], output
                ],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },

    });


    var DynamicPaMain = DynamicAccountReport.DynamicPaMain.extend({

        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.ageing_data = datas[1]
                self.period_dict = datas[2]
                self.period_list = datas[3]
                _.each(self.ageing_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    for (var z = 0; z < self.period_list.length; z++) {
                        k[self.period_list[z]] = self.formatWithSign(k[self.period_list[z]], formatOptions, k[self.period_list[z]] < 0 ? '-' : '');
                    }
                    k.total = self.formatWithSign(k.total, formatOptions, k.total < 0 ? '-' : '');
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPa', {
                        filter_data: self.filter_data,
                    }));
                    self.$el.find('#as_on_date').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Account Type...',
                    });
                    self.$el.find('.partner-type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Partner Type...',
                    });
                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Partner...',
                    });
                    self.$el.find('.partner-tag-multiple').select2({
                        placeholder: 'Select Tag...',
                    });
                    self.$el.find('.project-multiple').select2({
                        placeholder: 'Select Project...',
                    });
                    self.$el.find('.project-type-multiple').select2({
                        placeholder: 'Select Project Type...',
                    });
                    //Add Project Type Filter Onchange Event
                    self.$el.find(".project-type-multiple").on("change", function (e) {
                        //Remove currently selected projects
                        $('.project-multiple').select2('val', []);
                        //Get selected project types
                        let project_type_ids = $(this).val();
                        if (project_type_ids.length > 0) {
                            datas[0]['projects_list'].map(function(project){
                                let intersect_project_type_ids = project_type_ids.filter(function(project_type_id){
                                    return project[2].includes(parseInt(project_type_id));
                                });
                                if(intersect_project_type_ids.length > 0){
                                    $(".project-multiple").find("option[value='" + project[0] + "']").removeAttr('disabled');
                                }else{
                                    $(".project-multiple").find("option[value='" + project[0] + "']").attr("disabled", true);
                                }
                            });
                        }else{
                            $(".project-multiple").find("option").removeAttr('disabled');
                        }
                    });
                    self.$el.find(".project-type-multiple").trigger('change.select2');


                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val('include_details').trigger('change')
                    ;
                }
                self.$('.py-data-container-orig').html(QWeb.render('DataSectionPa', {
                    ageing_data: self.ageing_data,
                    period_dict: self.period_dict,
                    period_list: self.period_list
                }));
                self.loader_enable_ui();
            });
        },

        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {}
            output.type = false;
            output.include_details = false;
            output.partner_type = false;
            output.bucket_1 = $("#bucket_1").val();
            output.bucket_2 = $("#bucket_2").val();
            output.bucket_3 = $("#bucket_3").val();
            output.bucket_4 = $("#bucket_4").val();
            output.bucket_5 = $("#bucket_5").val();
            if ((parseInt(output.bucket_1) >= parseInt(output.bucket_2)) | (parseInt(output.bucket_2) >= parseInt(output.bucket_3)) |
                (parseInt(output.bucket_3) >= parseInt(output.bucket_4)) | (parseInt(output.bucket_4) >= parseInt(output.bucket_5))) {
                alert('Bucket order must be ascending');
                return;
            }
            if ($(".type-multiple").select2('data').length === 1) {
                output.type = $(".type-multiple").select2('data')[0].id
            }
            if ($(".partner-type-multiple").select2('data').length === 1) {
                output.partner_type = $(".partner-type-multiple").select2('data')[0].id
            }
            var partner_ids = [];
            var partner_list = $(".partner-multiple").select2('data')
            for (var i = 0; i < partner_list.length; i++) {
                partner_ids.push(parseInt(partner_list[i].id))
            }
            output.partner_ids = partner_ids
            var partner_tag_ids = [];
            var partner_tag_list = $(".partner-tag-multiple").select2('data')
            for (var i = 0; i < partner_tag_list.length; i++) {
                partner_tag_ids.push(parseInt(partner_tag_list[i].id))
            }
            output.partner_category_ids = partner_tag_ids
            if ($("#as_on_date").val()) {
                var dateObject = $("#as_on_date").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.as_on_date = dateString;
            }

            var project_ids = [];
            var projects_list = $(".project-multiple").select2('data')
            for (var i = 0; i < projects_list.length; i++) {
                project_ids.push(parseInt(projects_list[i].id))
            }
            output.project_ids = project_ids


            var proj_type_ids = [];
            var project_types_list = $(".project-type-multiple").select2('data')
            for (var i = 0; i < project_types_list.length; i++) {
                proj_type_ids.push(parseInt(project_types_list[i].id))
            }
            output.proj_type_ids = proj_type_ids

            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'include_details') {
                    output.include_details = true;
                }
            }
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
    });

    var DynamicPlMain = DynamicAccountReport.DynamicPlMain.extend({

        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.partner.ledger',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.account_data = datas[1]
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.ldate = field_utils.format.date(field_utils.parse.date(k.ldate, {}, {isUTC: true}));
                    _.each(k.lines, function (ks, vs) {
                        ks.debit = self.formatWithSign(ks.debit, formatOptions, ks.debit < 0 ? '-' : '');
                        ks.credit = self.formatWithSign(ks.credit, formatOptions, ks.credit < 0 ? '-' : '');
                        ks.balance = self.formatWithSign(ks.balance, formatOptions, ks.balance < 0 ? '-' : '');
                        ks.ldate = field_utils.format.date(field_utils.parse.date(ks.ldate, {}, {isUTC: true}));
                    });
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPl', {
                        filter_data: datas[0],
                    }));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val(['include_details', 'initial_balance']).trigger('change');
                    self.$el.find('.type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Account Type...',
                    });
                    self.$el.find('.reconciled-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Reconciled...',
                    });
                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Partner...',
                    });
                    self.$el.find('.partner-tag-multiple').select2({
                        placeholder: 'Select Tag...',
                    });
                    self.$el.find('.account-multiple').select2({
                        placeholder: 'Select Account...',
                    });
                    self.$el.find('.project-multiple').select2({
                        placeholder: 'Select Project...',
                    });
                    self.$el.find('.project-type-multiple').select2({
                        placeholder: 'Select Project Type...',
                    });
                    //Add Project Type Filter Onchange Event
                    self.$el.find(".project-type-multiple").on("change", function (e) {
                        //Remove currently selected projects
                        $('.project-multiple').select2('val', []);
                        //Get selected project types
                        let project_type_ids = $(this).val();
                        if (project_type_ids.length > 0) {
                            datas[0]['projects_list'].map(function(project){
                                let intersect_project_type_ids = project_type_ids.filter(function(project_type_id){
                                    return project[2].includes(parseInt(project_type_id));
                                });
                                if(intersect_project_type_ids.length > 0){
                                    $(".project-multiple").find("option[value='" + project[0] + "']").removeAttr('disabled');
                                }else{
                                    $(".project-multiple").find("option[value='" + project[0] + "']").attr("disabled", true);
                                }
                            });
                        }else{
                            $(".project-multiple").find("option").removeAttr('disabled');
                        }
                    });
                    self.$el.find(".project-type-multiple").trigger('change.select2');


                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                }
                self.$('.py-data-container-orig').html(QWeb.render('DataSectionPl', {
                    account_data: datas[1]
                }));
                self.loader_enable_ui();
            });
        },

        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range: false};
            output.type = false;
            output.display_accounts = 'balance_not_zero';
            output.initial_balance = false;
            output.balance_less_than_zero = false;
            output.balance_greater_than_zero = false;
            output.reconciled = false;
            output.include_details = false;
            if ($(".reconciled-multiple").select2('data').length === 1) {
                output.reconciled = $(".reconciled-multiple").select2('data')[0].id
            }
            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids
            var partner_ids = [];
            var partner_list = $(".partner-multiple").select2('data')
            for (var i = 0; i < partner_list.length; i++) {
                partner_ids.push(parseInt(partner_list[i].id))
            }
            output.partner_ids = partner_ids
            var partner_tag_ids = [];
            var partner_tag_list = $(".partner-tag-multiple").select2('data')
            for (var i = 0; i < partner_tag_list.length; i++) {
                partner_tag_ids.push(parseInt(partner_tag_list[i].id))
            }
            output.partner_category_ids = partner_tag_ids
            var account_ids = [];
            var account_list = $(".account-multiple").select2('data')
            for (var i = 0; i < account_list.length; i++) {
                account_ids.push(parseInt(account_list[i].id))
            }
            output.account_ids = account_ids

            var project_ids = [];
            var projects_list = $(".project-multiple").select2('data')
            for (var i = 0; i < projects_list.length; i++) {
                project_ids.push(parseInt(projects_list[i].id))
            }
            output.project_ids = project_ids

            var proj_type_ids = [];
            var project_types_list = $(".project-type-multiple").select2('data')
            for (var i = 0; i < project_types_list.length; i++) {
                proj_type_ids.push(parseInt(project_types_list[i].id))
            }
            output.proj_type_ids = proj_type_ids

            if ($(".date_filter-multiple").select2('data').length === 1) {
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            if ($(".type-multiple").select2('data').length === 1) {
                output.type = $(".type-multiple").select2('data')[0].id
            }
            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'initial_balance') {
                    output.initial_balance = true;
                }
                if (options_list[i].id === 'bal_not_zero') {
                    output.display_accounts = 'balance_not_zero';
                }
                if (options_list[i].id === 'include_details') {
                    output.include_details = true;
                }
                if (options_list[i].id === 'balance_less_than_zero') {
                    output.balance_less_than_zero = true;
                }
                if (options_list[i].id === 'balance_greater_than_zero') {
                    output.balance_greater_than_zero = true;
                }
            }
            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
            }
            self._rpc({
                model: 'ins.partner.ledger',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },

    });

    var DynamicTbMain = DynamicAccountReport.DynamicTbMain.extend({
        plot_data: function (initial_render = true) {
            var self = this;
            var node = self.$('.py-data-container');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.trial.balance',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0];
                self.account_data = datas[1];
                self.retained = datas[2];
                self.subtotal = datas[3];
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                _.each(self.retained, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                _.each(self.subtotal, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                self.filter_data.date_from_tmp = self.filter_data.date_from;
                self.filter_data.date_to_tmp = self.filter_data.date_to;
                self.filter_data.date_from = field_utils.format.date(field_utils.parse.date(self.filter_data.date_from, {}, {isUTC: true}));
                self.filter_data.date_to = field_utils.format.date(field_utils.parse.date(self.filter_data.date_to, {}, {isUTC: true}));
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionTb', {
                        filter_data: self.filter_data,
                    }));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    }).val('bal_not_zero').trigger('change');
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Select Analytic...',
                    });
                    self.$el.find('.project-multiple').select2({
                        placeholder: 'Select Project...',
                    });
                    self.$el.find('.project-type-multiple').select2({
                        placeholder: 'Select Project Type...',
                    });
                    //Add Project Type Filter Onchange Event
                    self.$el.find(".project-type-multiple").on("change", function (e) {
                        //Remove currently selected projects
                        $('.project-multiple').select2('val', []);
                        //Get selected project types
                        let project_type_ids = $(this).val();
                        if (project_type_ids.length > 0) {
                            datas[0]['projects_list'].map(function(project){
                                let intersect_project_type_ids = project_type_ids.filter(function(project_type_id){
                                    return project[2].includes(parseInt(project_type_id));
                                });
                                if(intersect_project_type_ids.length > 0){
                                    $(".project-multiple").find("option[value='" + project[0] + "']").removeAttr('disabled');
                                }else{
                                    $(".project-multiple").find("option[value='" + project[0] + "']").attr("disabled", true);
                                }
                            });
                        }else{
                            $(".project-multiple").find("option").removeAttr('disabled');
                        }
                    });
                    self.$el.find(".project-type-multiple").trigger('change.select2');


                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                    self.$el.find('.account-multiple').select2({
                        placeholder: 'Select Account...',
                    });
                }
                self.$('.py-data-container').html(QWeb.render('DataSectionTb', {
                    account_data: self.account_data,
                    retained: self.retained,
                    subtotal: self.subtotal,
                    filter_data: self.filter_data,
                }));
            });
        },


        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range: false};
            output.display_accounts = 'all';
            output.show_hierarchy = false;

            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids
            var account_ids = [];
            var account_list = $(".account-multiple").select2('data')
            for (var i = 0; i < account_list.length; i++) {
                account_ids.push(parseInt(account_list[i].id))
            }
            output.account_ids = account_ids
            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i = 0; i < analytic_list.length; i++) {
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            output.analytic_ids = analytic_ids
            if ($(".date_filter-multiple").select2('data').length === 1) {
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            var project_ids = [];
            var projects_list = $(".project-multiple").select2('data')
            for (var i = 0; i < projects_list.length; i++) {
                project_ids.push(parseInt(projects_list[i].id))
            }
            output.project_ids = project_ids

            var proj_type_ids = [];
            var project_types_list = $(".project-type-multiple").select2('data')
            for (var i = 0; i < project_types_list.length; i++) {
                proj_type_ids.push(parseInt(project_types_list[i].id))
            }
            output.proj_type_ids = proj_type_ids


            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'bal_not_zero') {
                    output.display_accounts = 'balance_not_zero';
                }
                if (options_list[i].id === 'show_hierarchy') {
                    output.show_hierarchy = true;
                }
            }
            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
            }
            self._rpc({
                model: 'ins.trial.balance',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },


    });

//    core.action_registry.add('dynamic.fr', DynamicFrMain);
//    core.action_registry.add('dynamic.gl', DynamicGlMain);
//    core.action_registry.add('dynamic.pa', DynamicPaMain);
//    core.action_registry.add('dynamic.pl', DynamicPlMain);
//    core.action_registry.add('dynamic.tb', DynamicTbMain);

});
