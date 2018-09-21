;(function (angular) {
  "use strict";

  var Annotation = buzz_data.Annotation;

  angular.module("page1")
         .component("page1", {

           "templateUrl": "/js/page1/page1.html",
           "controller": ['$http','$scope','$rootScope', '$state', '$q','$compile',

           function ($http,$scope,$rootScope,$state,$q,$compile) {
             var self = this;
             var color = $rootScope.color;
             var from_to = '/api/from_to/?'
             var static_data = '/api/static_production_data/?'
             var error_api = '/api/error_board'
             var def_disp = '/api/default'
             var project_dropdown_count = '/api/dropdown_data_types/?'
             var someDate = new Date();
             var fi_dd = someDate.getDate();
             var fi_mm = someDate.getMonth() + 1;
             var fi_y = someDate.getFullYear();
             var firstDate = fi_y + '-' + fi_mm + '-' + fi_dd;
             var numberOfDaysToSub = 6;
             someDate.setDate(someDate.getDate() - numberOfDaysToSub);
             var la_dd = someDate.getDate();
             var la_mm = someDate.getMonth() + 1;
             var la_y = someDate.getFullYear();
             var lastDate = la_y + '-' + la_mm + '-' + la_dd;
             var project = 'api/project/';
             var drop_down_link = '/api/dropdown_data/';
             var landing_pro = $state.params.selpro;
             self.pro_landing_url = 'api/project/?name='+landing_pro;
             var voice_filter_calls;

             self.project_live = ''
             self.center_live = ''

             $scope.singleModel = 1; 

             $scope.radioModel = 'Day';

             $scope.checkModel = {
                day: true,
                week: false,
                month: false
             };   
             
             var OneSignal = window.OneSignal || [];

                OneSignal.push(["init", {  
                  appId: "d0d6000e-27ee-459b-be52-d65ed4b3d025",
                  autoRegister: true, 
                  notifyButton: {
                    enable: true, /* Set to false to hide */
                    size: 'medium', /* One of 'small', 'medium', or 'large' */
                    theme: 'default', /* One of 'default' (red-white) or 'inverse" (white-red) */
                    position: 'bottom-left', /* Either 'bottom-left' or 'bottom-right' */
                    title: 'NextPulse', 
                    offset: {
                        bottom: '0px',
                        left: '0px', /* Only applied if bottom-left */
                        right: '0px' /* Only applied if bottom-right */
                    },
                    text: {
                        'dialog.main.title': 'NextPulse',
                    },
                  },
                  prenotify: true,
                  showCredit: false,
                  httpPermissionRequest: {
                    enable: false
                  },
                  welcomeNotification: {
                    "title": "NextPulse",
                    "message": "Thanks for subscribing!",
                    // "url": "" /* Leave commented for the notification to not open a window on Chrome and Firefox (on Safari, it opens to your webpage) */
                  },
                  displayPredicate: function() {
                    return OneSignal.isPushNotificationsEnabled()
                        .then(function(isPushEnabled) {
                            /* The user is subscribed, so we want to return "false" to hide the Subscription Bell */
                            return !isPushEnabled;
                        });
                 },
                 promptOptions: {
                    siteName: 'NextPulse',
                    /* actionMessage limited to 90 characters */
                    actionMessage: "We'd like to show you notifications for the latest news and updates.",
                    /* acceptButtonText limited to 15 characters */
                    acceptButtonText: "ALLOW",
                    /* cancelButtonText limited to 15 characters */
                    cancelButtonText: "NO THANKS"
                 }
                }]);
                OneSignal.push(function() {
                OneSignal.getUserId().then(function(userId) {
                    console.log("OneSignal User ID:", userId);
                    var user = userId;
                    var data = {};
                   data['userid'] = user;
                   $.ajax({url: '/api/notification/',
                           method: 'POST',
                           data: data,
                           'success': function(response) {
                            console.log(response);      
                        }
                    });
                });
            });

             $scope.checkResults = [];

             $scope.$watchCollection('checkModel', function () { 
                $scope.checkResults = [];
                angular.forEach($scope.checkModel, function (value, key) {
                    if (value) {
                        $scope.checkResults.push(key);

                    }
                });  
             });            

             
             self.annotations_data = {};

             self.add_loader = function() {
                    $('.widget-13a').addClass('widget-loader-show');
                    $('.widget-13b').addClass('widget-data-hide');
                    $('.widget-17a').addClass('widget-loader-show');
                    $('.widget-17b').addClass('widget-data-hide');
                    $('.widget-20a').addClass('widget-loader-show');
                    $('.widget-20b').addClass('widget-data-hide');
                    $('.widget-19a').addClass('widget-loader-show');
                    $('.widget-19b').addClass('widget-data-hide');
                    $('.widget-9a').addClass('widget-loader-show');
                    $('.widget-9b').addClass('widget-data-hide');
                    $('.widget-14a').addClass('widget-loader-show');
                    $('.widget-14b').addClass('widget-data-hide');
                    $('.widget-33a').addClass('widget-loader-show');
                    $('.widget-33b').addClass('widget-data-hide');
                    $('.widget-26a').addClass('widget-loader-show');
                    $('.widget-26b').addClass('widget-data-hide');
                    $('.widget-11a').addClass('widget-loader-show');
                    $('.widget-11b').addClass('widget-data-hide');
                    $('.widget-21a').addClass('widget-loader-show');
                    $('.widget-21b').addClass('widget-data-hide');
                    $('.widget-12a').addClass('widget-loader-show');
                    $('.widget-12b').addClass('widget-data-hide');
                    $('.widget-6a').addClass('widget-loader-show');
                    $('.widget-6b').addClass('widget-data-hide');
                    $('.widget-1a').addClass('widget-loader-show');
                    $('.widget-1b').addClass('widget-data-hide');
                    $('.widget-8a').addClass('widget-loader-show');
                    $('.widget-8b').addClass('widget-data-hide');
                    $('.widget-7a').addClass('widget-loader-show');
                    $('.widget-7b').addClass('widget-data-hide');
                    $('.widget-35a').addClass('widget-loader-show');
                    $('.widget-35b').addClass('widget-data-hide');
                    $('.widget-37a').addClass('widget-loader-show');
                    $('.widget-37b').addClass('widget-data-hide');
                    $('.widget-34a').addClass('widget-loader-show');
                    $('.widget-34b').addClass('widget-data-hide');
                    $('.widget-36a').addClass('widget-loader-show');
                    $('.widget-36b').addClass('widget-data-hide');
                    $('.widget-4a').addClass('widget-loader-show');
                    $('.widget-4b').addClass('widget-data-hide');
                    $('.widget-5a').addClass('widget-loader-show');
                    $('.widget-5b').addClass('widget-data-hide');
                    $('.widget-3a').addClass('widget-loader-show');
                    $('.widget-3b').addClass('widget-data-hide');
                    $('.widget-2a').addClass('widget-loader-show');
                    $('.widget-2b').addClass('widget-data-hide');
                    $('.widget-23a').addClass('widget-loader-show');
                    $('.widget-23b').addClass('widget-data-hide');
                    $('.widget-22a').addClass('widget-loader-show');
                    $('.widget-22b').addClass('widget-data-hide');
                    $('.widget-24a').addClass('widget-loader-show');
                    $('.widget-24b').addClass('widget-data-hide');
                    $('.widget-25a').addClass('widget-loader-show');
                    $('.widget-25b').addClass('widget-data-hide');
                    $('.widget-38a').addClass('widget-loader-show');
                    $('.widget-38b').addClass('widget-data-hide');
                    $('.widget-39a').addClass('widget-loader-show');
                    $('.widget-39b').addClass('widget-data-hide');
                    $('.widget-60a').addClass('widget-loader-show');
                    $('.widget-60b').addClass('widget-data-hide');
                    $('.widget-62a').addClass('widget-loader-show');
                    $('.widget-62b').addClass('widget-data-hide');
                    $('.widget-64a').addClass('widget-loader-show');
                    $('.widget-64b').addClass('widget-data-hide');
                    $('.widget-65a').addClass('widget-loader-show');
                    $('.widget-65b').addClass('widget-data-hide');
             }

             self.apply_class = function(){

                    if ((self.day_type === 'week') || (self.sel_type === 'week')){
                        $('.week2').addClass('active btn-success');
                        $('.week2').siblings().removeClass('active btn-success');
                        $('.week').addClass('active btn-success');
                        $('.week').siblings().removeClass('active btn-success');
                    }
                    if ((self.day_type === 'month') || (self.sel_type === 'month')){
                        $('.month2').addClass('active btn-success');
                        $('.month2').siblings().removeClass('active btn-success');
                        $('.month').addClass('active btn-success');
                        $('.month').siblings().removeClass('active btn-success');
                    }
                    if ((self.day_type === 'day') || (self.sel_type === 'day')){
                        $('.day2').addClass('active btn-success');
                        $('.day2').siblings().removeClass('active btn-success');
                        $('.day').addClass('active btn-success');
                        $('.day').siblings().removeClass('active btn-success');
                    }            
            }               

            self.checkScroll = function() {
                if($('.scroll').scrollTop() == 0) {
                    $('.fa-arrow-circle-o-up').addClass('hide');
                } else {
                    $('.fa-arrow-circle-o-up').removeClass('hide');
                }
            }
 
             $('#annotation_button').click(function(){

                var hasAnnotations = $("body").hasClass("add_annotation");

                $("body")[!hasAnnotations ? "addClass"
                                          : "removeClass"]('add_annotation');
             });

             $('#select').daterangepicker({
                    "autoApply": true,
                    "locale": {
                        "format": 'YYYY-MM-DD',
                        "separator": ' to '
                    },
              }, function(start, end, label) {
                var callback = [];
                self.start = start.format('YYYY-MM-DD');
                self.end = end.format('YYYY-MM-DD');
                $('.input-sm').prop('selectedIndex',0);
              
                self.add_loader();

                callback.push.apply(callback, [self.start, self.end, self.center_live, self.project_live])
                self.apply_class();
                if(self.is_voice_flag) {
                    self.voiceTypeFilter(self.voiceProjectType, 1);
                } else {
                    var dateEntered = document.getElementById('select').value;
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    callback.push.apply(callback, [from, to, self.center_live, self.project_live]);
                    var packet_url = '/api/get_packet_details/?&project='+callback[3]+'&center='+callback[2]+'&from='+self.start+'&to='+self.end+'&voice_project_type=';
                    $http.get(packet_url).then(function(result) {
                        self.global_packet_values = result.data.result.fin;
                        self.drop_list = [];
                        self.top_employee_details =  result.data.result.top_five_employee_details;
                        self.top_five = result.data.result.only_top_five;
                        self.volume_graphs = result.data.result.volumes_graphs_details;
                        self.drop_list =  result.data.result.drop_value;
                        if ( self.is_voice_flag == false) {
                            self.sub_pro_sel = document.getElementById("0");
                            self.wor_pac_sel = document.getElementById("1");
                            self.sub_pac_sel = document.getElementById("2");
                            $(self.sub_pro_sel.options).remove();
                            self.sub_pro_sel.options[self.sub_pro_sel.options.length] = new Option('All', 'All');
                            for (var sub_pro in self.drop_list) {
                                self.sub_pro_sel.options[self.sub_pro_sel.options.length] = new Option(sub_pro, sub_pro);
                            }
                        }
                        self.checkScroll();
                    })
                    self.main_widget_function(callback, '');
                }
                //self.main_widget_function(callback, '');
                $('.widget17b').addClass('widget-data-hide');

               });

                
                $('#date-selector').daterangepicker({
                    'autoApply':true,
                }, function(start, end){
                  $('#date-selector-modal').slideUp(400);
                  $('.modal-backdrop').remove();
                  self.start_date = start.format('YYYY-MM-DD');
                  self.end_date = end.format('YYYY-MM-DD');
                  var today_date = new Date();
                  today_date = today_date.getMonth()+1+'/'+today_date.getDate()+'/'+today_date.getFullYear();
                  $('#date-selector').data('daterangepicker').setStartDate(today_date);
                  $('#date-selector').data('daterangepicker').setEndDate(today_date);
                  if(new Date(self.end_date) > new Date(self.last)|| new Date(self.start_date) > new Date(self.last)){
                    swal({
                      title:"Please select valid date.",
                      icon:"warning",
                      text:"latest date: "+ self.last
                    });
                  } else {
                    window.open('/js/page1/intelligence.audit.html?widget_data='+self.static_widget_data+'&from='+self.start_date+'&to='+self.end_date);
                  }                    
                });

            //Voice Type User
            self.filter_list = ['location', 'skill', 'disposition', 'call_status', 'cate_dispo_inbound', 'outbound_dispo_cate', 'outbound_disposition', 'outbnd_dispo_common', 'inbnd_utilization', 'outbnd_utilization', 'inbnd_occupancy', 'outbnd_occupancy', 'inbound_productivity', 'outbound_productivity', 'utilization', 'occupancy', 'agent_productivity_data', 'agent_required'];
            self.chartType = ['bar', 'stacked', 'pie', 'line'];
            self.voice_widget_function = function(result, voiceFilterType, widgetA, widgetB) {
                var chartOptions, chartSeries, chartType;
                if(voiceFilterType == self.filter_list[0]) {
                    chartOptions = self.chartOptions47;
                    chartSeries = result.result[self.filter_list[0]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[1]) {
                    chartOptions = self.chartOptions48;
                    chartSeries = result.result[self.filter_list[1]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[2]) {
                    chartOptions = self.chartOptions49;
                    chartSeries = result.result[self.filter_list[2]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[3]) {
                    chartOptions = self.chartOptions50;
                    chartSeries = result.result[self.filter_list[3]];
                    chartType = self.chartType[1];
                } else if (voiceFilterType == self.filter_list[4]) {
                    chartOptions = self.chartOptions51;
                    chartSeries = result.result[self.filter_list[4]];
                    chartType = self.chartType[2];
                } else if (voiceFilterType == self.filter_list[5]) {
                    chartOptions = self.chartOptions52;
                    chartSeries = result.result[self.filter_list[5]];
                    chartType = self.chartType[2];
                } else if (voiceFilterType == self.filter_list[6]) {
                    chartOptions = self.chartOptions53;
                    chartSeries = result.result[self.filter_list[6]];
                    chartType = self.chartType[0];  
                } else if (voiceFilterType == self.filter_list[7]) {
                    chartOptions = self.chartOptions54;
                    chartSeries = result.result[self.filter_list[7]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[8]) {
                    chartOptions = self.chartOptions55;
                    chartSeries = result.result[self.filter_list[8]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[9]) {
                    chartOptions = self.chartOptions56;
                    chartSeries = result.result[self.filter_list[9]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[10]) {
                    chartOptions = self.chartOptions57;
                    chartSeries = result.result[self.filter_list[10]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[11]) {
                    chartOptions = self.chartOptions58;
                    chartSeries = result.result[self.filter_list[11]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[12]) {
                    chartOptions = self.chartOptions59;
                    chartSeries = result.result[self.filter_list[12]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[13]) {
                    chartOptions = self.chartOptions60;
                    chartSeries = result.result[self.filter_list[13]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[14]) {
                    chartOptions = self.chartOptions61;
                    chartSeries = result.result[self.filter_list[14]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[15]) {
                    chartOptions = self.chartOptions62;
                    chartSeries = result.result[self.filter_list[15]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[16]) {
                    chartOptions = self.chartOptions63;
                    chartSeries = result.result[self.filter_list[16]];
                    chartType = self.chartType[0];
                } else if (voiceFilterType == self.filter_list[17]) {
                    chartOptions = self.chartOptions64;
                    chartSeries = result.result[self.filter_list[17]];
                    chartType = self.chartType[0];
                }
                switch (chartType) {
                    case self.chartType[1]:
                        angular.extend(chartOptions, {
                            xAxis: {
                                categories: result.result.date,
                            },
                            plotOptions: {
                                column: {
                                    stacking: 'normal',
                                    dataLabels: {
                                        enabled: true,
                                        color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'black'
                                    }
                                }
                            },
                            series: chartSeries
                        })
                        break;
                    case self.chartType[2]:
                        angular.extend(chartOptions, {
                            series: [{
                                name: '',
                                colorByPoint: true,
                                data: chartSeries
                            }]
                        })
                        break;
                    default:
                        //Bar
                        angular.extend(chartOptions, {
                            xAxis: {
                                categories: result.result.date,
                            },
                            plotOptions: {
                                series: {
                                  dataLabels: {
                                    enabled: true,
                                    formatter: function () {
                                        return Highcharts.numberFormat(this.y, null, null, ",");
                                    }
                                  },
                                  allowPointSelect: true,
                                  cursor: 'pointer',
                                }
                            },
                            series: chartSeries
                        })
                }
                $(widgetA).removeClass('widget-loader-show');
                $(widgetB).removeClass('widget-data-hide');
            }

             self.highlightTypes = function (button_type, widgetName) {
                $(widgetName + ' .' + button_type + '2').addClass('active btn-success');
                $(widgetName + ' .' + button_type + '2').siblings().removeClass('active btn-success');
             }

             self.main_widget_function = function(callback, packet) {
                    
                    self.center_live = callback[2];

                    self.project_live = callback[3];
                    self.start_date = callback[0];
                    self.end_date = callback[1];

                    $('#emp_widget').hide();

                    $('#volume_table').hide();

                    if (self.user_status === 'Invalid User') {
                        swal({
                            title: 'Your Not Authorised for ' + self.project_live,
                            showConfirmButton: false
                        });
                        window.location = window.location.origin;
                    }
                   
                    self.data_to_show = '?&project='+callback[3]+'&center='+callback[2]+'&from='+ callback[0]+'&to='+ callback[1]+packet+'&type=';
                    self.aht_data_to_show = '?&project='+callback[3]+'&center='+callback[2]+'&from='+ callback[0]+'&to='+ callback[1] + '&type=';
                    self.static_widget_data = '&project='+callback[3]+'&center='+callback[2]
                    self.common_for_all = self.data_to_show + self.day_type;
                    var error_bar_graph = '/api/error_bar_graph/'+self.common_for_all;
                    var err_field_graph = '/api/err_field_graph/'+self.common_for_all;
                    var cate_error = '/api/cate_error/'+self.common_for_all;
                    var pareto_cate_error = '/api/pareto_cate_error/'+self.common_for_all;
                    var agent_cate_error = '/api/agent_cate_error/'+self.common_for_all;
                    var nw_exce = '/api/nw_exce/'+self.common_for_all;
                    var overall_exce = '/api/overall_exce'+self.common_for_all;

                    self.ajax_for_role = function() {

                      $http({method: "GET", url: self.pro_landing_url}).success(function(result){

                        self.role_for_perm = result.result.role;
                        
                      });
                    }

                    self.ajax_for_role();

                    var dateEntered = document.getElementById('select').value;
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');

                    self.annot_perm = function() {

                        if (self.role_for_perm === "customer") {

                          $('.annotation-popover').find('p').attr('contenteditable', 'false');
                          $('.popover-title').hide();
                          //$('.icon-action-group').hide()
                        }
                        else {

                          $('.annotation-popover').find('p').attr('contenteditable', 'true');
                          $('.popover-title').show();
                          //$('.icon-action-group').show()
                        }
                    }

                    self.allo_and_comp = function(final_work, type, name) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        if (name == undefined) {
                            name = ''
                        }

                        self.type = type;

                        if ((self.work_list.length == 1) || (type == 'week') || (type == 'month') || (self.button_clicked == "day_yes")) {

                        var allo_and_comp = '/api/alloc_and_compl/'+self.data_to_show + type + final_work+'&chart_name=17&chart_name=13';

                        return $http({method:"GET", url: allo_and_comp}).success(function(result){
                           var is_annotation = result.result.is_annotation; 
                           if ((name == "self.chartOptions17") || (name == "")) {
                                $('.widget-17a').removeClass('widget-loader-show');
                                $('.widget-17b').removeClass('widget-data-hide');
                            }
                           if ((name == "self.chartOptions18") || (name == "")) {
                                $('.widget-13a').removeClass('widget-loader-show');
                                $('.widget-13b').removeClass('widget-data-hide');
                            }
                            
                            if (type == 'day' && final_work == '') {
                                if (result.result.type == 'day') {
                                    $('.day2').addClass('active btn-success');
                                    $('.day2').siblings().removeClass('active btn-success');
                                    $('.day').addClass('active btn-success');
                                    $('.day').siblings().removeClass('active btn-success');
                                }
                               
                                if (result.result.type == 'week') {
                                    $('.week2').addClass('active btn-success');
                                    $('.week2').siblings().removeClass('active btn-success');
                                    $('.week').addClass('active btn-success');
                                    $('.week').siblings().removeClass('active btn-success');
                                }

                                if (result.result.type == 'month') {
                                    $('.month2').addClass('active btn-success');
                                    $('.month2').siblings().removeClass('active btn-success');
                                    $('.month').addClass('active btn-success');
                                    $('.month').siblings().removeClass('active btn-success');
                                }
                            }
                            var date_list = result.result.date;
                            var data_list_bar = result.result.volume_graphs.bar_data;
                            var data_list_line = result.result.volume_graphs.line_data;

                            if ((name == "self.chartOptions17") || (name == "")) {

                                if (self.list_object.volume_bar_graph != undefined) {

                                    if(self.list_object.volume_bar_graph.display_value === true) {
                                    
                                        var value = true;

                                    }

                                    else {
                                        var value = false;    
                                    }
                                }

                                else {
                                    var value = false;
                                }

                                if (self.list_object.volume_bar_graph != undefined) {

                                    if(self.list_object.volume_bar_graph.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';

                                    }

                                    else if(self.list_object.volume_bar_graph.legends_align == 'left'){

                                        var align = 'left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }

                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }

                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }

                                var graph_name = 'self.chartOptions17';
                                angular.extend(self.chartOptions17, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                            formatter: function () {
                                                return Highcharts.numberFormat(this.y, null, null, ",");
                                            }
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                          point: {
                                              events:{
                                                
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) { 
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '17<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions17.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                          },
                                          events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var show = this.visible;
                                                    var chart_name = self.bar_series_name;
                                                    self.annotObj.forEach(function(value_data){
                                                        value_data.redraw(name, show);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-17a').children(".widget-17b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name = this.name;
                                                    var show = this.visible;
                                                    var chart_name = self.bar_series_name;
                                                    self.annotObj.forEach(function(value_data){
                                                        value_data.redraw(name, show);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-17a').children(".widget-17b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                            }
                                        }
                                    },   
                                    series: data_list_bar,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                        var series = null;
                                        var chart_data = chart.series;
                                        self.annotObj = [];
                                        self.bar_series_name = [];
                                        for(var i in chart_data){
                                            series = chart_data[i];
                                            (function(series){
                                            $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=17&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                                annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                                $.each(annotations, function(j, annotation){

                                var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                point = point[0];
                                if(annotation.epoch){
                                   var a = new Annotation("17", $(self.chartOptions17.chart.renderTo),
                                        chart, point, annotation);
                                   self.annotObj.push(a);
                                   window.annotObj = a;
                                   self.bar_series_name.push(series.name);  
                                   self.annot_perm();
                                   
                                }
                               })
                                        });
                                        }(series));
                                    }
                                    }
                                  }
                                })
                            }

                            if ((name == "self.chartOptions18") || (name == "")) {

                                if (self.list_object.volume_productivity_graph != undefined) {

                                    if(self.list_object.volume_productivity_graph.display_value === true) {
                                    
                                        var value = true;

                                    }
                                    else {
                                        var value = false;    
                                    }
                                }

                                else {
                                    var value = false;
                                }
                                if (self.list_object.volume_productivity_graph != undefined) {

                                    if(self.list_object.volume_productivity_graph.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.volume_bar_graph.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }
                                var graph_name = "self.chartOptions18";
                                angular.extend(self.chartOptions18, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                            formatter: function () {
                                               return Highcharts.numberFormat(this.y, null, null, ",");
                                            }
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '13<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions18.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            },
                                            events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self.line_allo_data;
                                                    self.object_data.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >=0 ) {
                                                        $(document).find('.widget-13a').children(".widget-13b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);   
                                                    }
                                                },
                                                show: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self.line_allo_data;
                                                    self.object_data.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >=0 ) {
                                                        $(document).find('.widget-13a').children(".widget-13b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);   
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    series: data_list_line,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                        var series = null;
                                        var chart_data = chart.series;
                                        self.object_data = [];
                                        self.line_allo_data = [];
                                        for(var i in chart_data){
                                            series = chart_data[i];
                                            (function(series){
                                            $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                                    self.type+'&chart_name=13&project='+self.project_live+'&center='+
                                    self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                                    annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                                    $.each(annotations, function(j, annotation){

                                    var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                    point = point[0];

                                    if(annotation.epoch){
                                        var a = new Annotation("13", $(self.chartOptions18.chart.renderTo),
                                            chart, point, annotation);
                                    window.object_data = a;
                                    self.object_data.push(a);
                                    self.line_allo_data.push(series.name);
                                    self.annot_perm();
                                   }
                                })

                                        });
                                        }(series));
                                    }
                                    }
                                  }
                                });
                           }
                        })
                      }
                    }

                    self.utill_all = function(final_work, type,name) {
                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        if (name == undefined) {
                            name = ''
                        }
            
                        self.type = type;

                        if ((self.utili_list.length == 1) || (type == 'week') || (type == 'month') || (self.button_clicked == "day_yes")) {

                        var utill_all = '/api/utilisation_all/'+self.data_to_show + type + final_work+'&chart_name=20&chart_name=19&chart_nam=9';

                        return $http({method:"GET", url: utill_all}).success(function(result){

                            var date_list  = result.result.date;
                            var utili_opera_data = result.result.utilization_operational_details;
                            var utili_fte_data = result.result.utilization_fte_details;
                            var overall_utili_data = result.result.original_utilization_graph;
                            var is_annotation = result.result.is_annotation;

                            angular.extend(self.chartOptions25.yAxis,{
                               min:result.result.min_utilization_operational_details,
                               max:result.result.max_utilization_operational_details
                            });

                            angular.extend(self.chartOptions24.yAxis,{
                                min:result.result.min_utilization_fte_details,
                                max:result.result.max_utilization_fte_details
                            });      

                            angular.extend(self.chartOptions15.yAxis,{
                                min:result.result.min_original_utilization_graph,
                                max:result.result.max_original_utilization_graph
                            });      

                            if ((name == "self.chartOptions25") || (name == "")) {
                                
                                if (self.list_object.operational_utilization != undefined) {

                                    if (self.list_object.operational_utilization.display_value === true) {

                                        var value = true;
                                    }

                                    else {
                                    
                                        var value = false;
                                    }

                                }
                                else {

                                    var value = false;
                                }
                                if (self.list_object.operational_utilization != undefined) {

                                    if(self.list_object.operational_utilization.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.operational_utilization.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }

                                angular.extend(self.chartOptions25, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                            
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '20<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions25.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            }
                                        }
                                    },
                                    series: utili_opera_data,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=20&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("20", $(self.chartOptions25.chart.renderTo),
                                        chart, point, annotation);
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                   } 
                                });
                            
                                $('.widget-20a').removeClass('widget-loader-show');
                                $('.widget-20b').removeClass('widget-data-hide');
                            }
                            
                            if ((name == "self.chartOptions24") || (name == "")) {

                                if (self.list_object.fte_utilization != undefined) {

                                    if (self.list_object.fte_utilization.display_value === true) {

                                        var value = true;
                                    }

                                    else {

                                        var value = false;    
                                    }
                                }
                                else {

                                    var value = false;
                                }
                            if (self.list_object.fte_utilization != undefined) {

                                    if(self.list_object.fte_utilization.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.fte_utilization.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }

                                angular.extend(self.chartOptions24, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                            
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                          },  
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: { 
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                var str = '19<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions24.chart.renderTo),this.series.chart, this);
                                                    }
                                                   }
                                                }
                                            }
                                        }
                                    },

                                    series: utili_fte_data,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=19&project='+self.project_live+'&center='+
                              self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("19", $(self.chartOptions24.chart.renderTo),
                                        chart, point, annotation);
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                  }  
                                });
                                $('.widget-19a').removeClass('widget-loader-show');
                                $('.widget-19b').removeClass('widget-data-hide');
                            }

                            if ((name == "self.chartOptions15") || (name == "")) {

                                if (self.list_object.utilisation_wrt_work_packet != undefined) {

                                    if (self.list_object.utilisation_wrt_work_packet.display_value === true) {

                                        var value = true;
                                    }
                                    else {
                                        var value = false;    
                                    }
                                }
                                else {
                                    var value = false;
                                }
                                if (self.list_object.utilisation_wrt_work_packet != undefined) {

                                    if(self.list_object.utilisation_wrt_work_packet.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.utilisation_wrt_work_packet.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }
                                angular.extend(self.chartOptions15, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                                     plotOptions: {
                                     series: {
                                        dataLabels: {
                                         enabled: value,
                                       },
                                       allowPointSelect: true,
                                       cursor: 'pointer',
                                         point: { 
                                           events:{
                                         contextmenu: function() {
                                         if (self.role_for_perm == 'customer') {

                                            console.log('he is customer');
                                         }
                                         else {

                                           if (self.data_to_show.split('&').length == 6) {
                                             var sub_proj = '';
                                             var work_pack = '';
                                             var sub_pack = '';
                                           }
                                           else {
                                             var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                             var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                             var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                           }
                                                 var str = '9<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                                    this['project'] = self.project_live;
                                                                    this['center'] = self.center_live;
                                                                    this['from'] = self.start_date;
                                                                    this['to'] = self.end_date;
                                             return new Annotation(str, $(self.chartOptions15.chart.renderTo),this.series.chart, this);
                                             }
                                            }
                                         }
                                         }
                                     }
                                     },

                                    series: overall_utili_data,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
       
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=9&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){
       
                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});
       
                                 point = point[0];
       
                                 if(annotation.epoch){
                                   var a = new Annotation("9", $(self.chartOptions15.chart.renderTo),
                                        chart, point, annotation);
                                   self.annot_perm();   
                                   }
                               })
       
                                        });
                                        }(series));
                                    }
                                    }
                                  }
                                });
                               $('.widget-9a').removeClass('widget-loader-show');
                               $('.widget-9b').removeClass('widget-data-hide');
                            }
                        })
                      }  
                    }
                    
                    self.productivity = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var productivity = '/api/productivity/'+self.data_to_show + type + final_work + '&chart_name=14';

                        return $http({method:"GET", url: productivity}).success(function(result){

                            var date_list = result.result.date;
                            var productivity = result.result.productivity;
                            var is_annotation = result.result.is_annotation;                            

                            if (self.list_object.productivity_trends != undefined) {

                                if (self.list_object.productivity_trends.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    
                                    var value = false;    
                                }
                            }
                            else {
                                var value = false;
                            }
                            if (self.list_object.productivity_trends != undefined) {

                                if(self.list_object.productivity_trends.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.productivity_trends.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }

                            angular.extend(self.chartOptions19, {
                                xAxis: {
                                    categories: date_list,
                                },
                                legend: {
                                    align: align,
                                    verticalAlign:ver_align,
                                    layout: layout
                                },
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '14<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions19.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            },
                                            events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._productivity_data;
                                                    self.data_anno.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-14a').children(".widget-14b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._productivity_data;
                                                    self.data_anno.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-14a').children(".widget-14b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                            }
                                        }
                                    },

                                series: productivity,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self.data_anno = [];
                                    self._productivity_data = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=14&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("14", $(self.chartOptions19.chart.renderTo),
                                        chart, point, annotation);
                                   window.data_anno = a;
                                   self.data_anno.push(a);
                                   self._productivity_data.push(series.name);
                                   self.annot_perm();
                                   }
                               })   

                                        });
                                        }(series));
                                    }
                                    }
                                }
                            });
                            $('.widget-14a').removeClass('widget-loader-show');
                            $('.widget-14b').removeClass('widget-data-hide');
                        })
                    }

                    self.prod_avg = function(final_work, type) {
 
                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }
 
                        self.type = type;

                        var prod_avg = '/api/prod_avg_perday/'+self.data_to_show + type + final_work + '&chart_name=33';

                        return $http({method:"GET", url: prod_avg}).success(function(result){

                           var date_list = result.result.date;
                           var prod_avg_data = result.result.production_avg_details;
                           var is_annotation = result.result.is_annotation; 

                            if (self.list_object.production_avg_perday != undefined) {

                                if (self.list_object.production_avg_perday.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;   
                                }
                            }
                            else {
                                var value = false;
                            }
                            if (self.list_object.production_avg_perday != undefined) {

                                if(self.list_object.production_avg_perday.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.production_avg_perday.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }
                           angular.extend(self.chartOptions38, {
                                xAxis: {
                                    categories: date_list,
                                },
                                legend: {
                                    align: align,
                                    verticalAlign:ver_align,
                                    layout: layout
                                },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                         enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                    point: {
                                      events:{
                                        contextmenu: function() {
                                         if (self.role_for_perm == 'customer') {

                                            console.log('he is customer');
                                         }
                                         else {

                                          if (self.data_to_show.split('&').length == 6) {
                                        var sub_proj = '';
                                        var work_pack = '';
                                        var sub_pack = '';
                                          }
                                          else {
                                            var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                        var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                        var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                          }
                                                var str = '33<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                                this['project'] = self.project_live;
                                                                this['center'] = self.center_live;
                                                                this['from'] = self.start_date;
                                                                this['to'] = self.end_date;
                                          return new Annotation(str, $(self.chartOptions38.chart.renderTo),this.series.chart, this);
                                            }
                                          }
                                        }
                                        },
                                        events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._prod_avg;
                                                    self.anno_obj.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-33a').children(".widget-33b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name =  this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._prod_avg
                                                    self.anno_obj.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-33a').children(".widget-33b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                        }
                                    }
                                    },
                                series: prod_avg_data,
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;
                                self.anno_obj = [];
                                self._prod_avg = [];
                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=33&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){
       
                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("33", $(self.chartOptions38.chart.renderTo),
                                    chart, point, annotation);
                               window.anno_obj = a;
                               self.anno_obj.push(a);
                               self._prod_avg.push(series.name);
                               self.annot_perm();
                               }
                           })

                                    });
                                    }(series));
                                }
                                }
                              }  
                            });
                            $('.widget-33a').removeClass('widget-loader-show');
                            $('.widget-33b').removeClass('widget-data-hide');
                       }) 
                    }

                    self.tat_data = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var tat_data = '/api/tat_data/'+ self.data_to_show + type + final_work + '&chart_name=26';

                        return $http({method:"GET", url: tat_data}).success(function(result){

                            var date_list = result.result.date;
                            var tat_values = result.result.tat_graph_details;
                            var is_annotation = result.result.is_annotation;                            

                            if (self.list_object.tat_graph != undefined) {

                                if (self.list_object.tat_graph.display_value === true) {
                                      
                                    var value = true
                                }
                                else {
                                    var value = false
                                }
                            }
                            else {
                                
                                var value = false
                            }
                            if (self.list_object.tat_graph != undefined) {

                                if(self.list_object.tat_graph.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.tat_graph.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }

                            angular.extend(self.chartOptions31.yAxis,{
                               min:result.result.min_max.min_value,
                               max:result.result.min_max.max_value
                            })

                            angular.extend(self.chartOptions31, {
                                xAxis: {
                                    categories: date_list,
                                },
                                legend: {
                                    align: align,
                                    verticalAlign:ver_align,
                                    layout: layout
                                },                        
                                plotOptions: {
                                    series: {
                                        dataLabels: {
                                            enabled: value,
                                        },
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '26<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions31.chart.renderTo),this.series.chart, this);
                                                    }
                                                }
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                var name =  this.name;
                                                var visibility = this.visible;
                                                var chart_name = self._tat_data;
                                                self.anno_value.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-26a').children(".widget-26b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                }
                                            },
                                            show: function() {
                                                var name =  this.name;
                                                var visibility = this.visible;
                                                var chart_name = self._tat_data;
                                                self.anno_value.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-26a').children(".widget-26b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                }
                                            }
                                        }
                                    }
                                },

                                series: tat_values,
                                onComplete: function(chart){
                                if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self.anno_value = [];
                                    self._tat_data = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                                                self.type+'&chart_name=26&project='+self.project_live+'&center='+
                                                self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                                                    annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                                                     $.each(annotations, function(j, annotation){

                                                       var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                                       point = point[0];

                                                       if(annotation.epoch){
                                                         var a = new Annotation("26", $(self.chartOptions31.chart.renderTo),
                                                              chart, point, annotation);
                                                         window.anno_value = a;
                                                         self.anno_value.push(a);
                                                         self._tat_data.push(series.name);
                                                         self.annot_perm();
                                                         }
                                                     })   

                                                });
                                        }(series));
                                    }
                                }
                                }
                            });
                            $('.widget-26a').removeClass('widget-loader-show');
                            $('.widget-26b').removeClass('widget-data-hide');
                        })
                    }


                    self.aht_data = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var aht_data = '/api/aht_team_data/'+ self.data_to_show + type + final_work + '&chart_name=60';

                        return $http({method:"GET", url: aht_data}).success(function(result){

                            var date_list = result.result.date;
                            var aht_data = result.result.aht_team_data;
                            var is_annotation = result.result.is_annotation;                            

                            if (self.list_object.aht_team_grpah != undefined) {

                                if (self.list_object.aht_team_grpah.display_value === true) {
     
                                    var value = true 
                                }
                                else {
                                    var value = false
                                }
                            }
                            else {
     
                                var value = false
                            }
                            if (self.list_object.aht_team_grpah != undefined) {

                                if(self.list_object.aht_team_grpah.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.aht_team_grpah.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }
                            angular.extend(self.chartOptions65.yAxis,{
                               min:result.result.min_max.min_value,
                               max:result.result.min_max.max_value
                            });

                            angular.extend(self.chartOptions65, {
                                xAxis: {
                                    categories: date_list,
                                },
                                legend: {
                                    align: align,
                                    verticalAlign:ver_align,
                                    layout: layout
                                },
                        
                                plotOptions: {
                                    series: {
                                        dataLabels: {
                                            enabled: value,
                                        },
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '60<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions65.chart.renderTo),this.series.chart, this);
                                                    }
                                                }
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                var name =  this.name;
                                                var visibility =  this.visible;
                                                var chart_name = self._aht_data;
                                                self.value_anno.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-60a').children(".widget-60b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                }
                                            },
                                            show: function() {
                                                var name =  this.name;
                                                var visibility =  this.visible;
                                                var chart_name = self._aht_data;
                                                self.value_anno.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-60a').children(".widget-60b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                }
                                            }
                                        }
                                    }
                                },

                                series: aht_data,
                                onComplete: function(chart){
                                if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self.value_anno = [];
                                    self._aht_data = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                                                self.type+'&chart_name=60&project='+self.project_live+'&center='+
                                                self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                                                    annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                                                     $.each(annotations, function(j, annotation){

                                                       var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                                       point = point[0];

                                                       if(annotation.epoch){
                                                         var a = new Annotation("60", $(self.chartOptions65.chart.renderTo),
                                                              chart, point, annotation);
                                                         window.value_anno = a;
                                                         self.value_anno.push(a);
                                                         self._aht_data.push(series.name);
                                                         self.annot_perm();
                                                         }
                                                     })   

                                                });
                                        }(series));
                                    }
                                }
                                }
                            });
                            $('.widget-60a').removeClass('widget-loader-show');
                            $('.widget-60b').removeClass('widget-data-hide');
                        })
                    }

                    self.mont_volume = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var mont_volume = '/api/monthly_volume/'+self.data_to_show + type + final_work + '&chart_name=21';

                        return $http({method:"GET", url: mont_volume}).success(function(result){

                            var date_list  = result.result.date;

                            var monthly_volume = result.result.monthly_volume_graph_details;
                            var is_annotation = result.result.is_annotation;

                            if (self.list_object.monthly_volume_widget != undefined) {
                            
                                if (self.list_object.monthly_volume_widget.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                            if (self.list_object.monthly_volume_widget != undefined) {

                                if(self.list_object.monthly_volume_widget.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.monthly_volume_widget.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }

                            angular.extend(self.chartOptions26, {
                                xAxis: {
                                    categories: date_list,
                                },
                                legend: {
                                    align: align,
                                    verticalAlign:ver_align,
                                    layout: layout
                                },                                
                                    plotOptions: {
                                        series: {
                                        dataLabels: {
                                            enabled: value,
                                        },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{ 
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '21<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions26.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            },
                                            events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._month_vol;
                                                    self.annotation.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-21a').children(".widget-21b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._month_vol;
                                                    self.annotation.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-21a').children(".widget-21b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                            }
                                        }
                                    },
                                series: monthly_volume,
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;
                                self.annotation = [];
                                self._month_vol = [];
                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=21&project='+self.project_live+'&center='+
                          self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){
       
                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});
       
                             point = point[0];
       
                             if(annotation.epoch){
                               var a = new Annotation("21", $(self.chartOptions26.chart.renderTo),
                                    chart, point, annotation);
                               window.annotation = a;
                               self.annotation.push(a);
                               self._month_vol.push(series.name);
                               self.annot_perm();
                               }
                           })
       
                                    });
                                   }(series));
                                }
                                }
                              }  
                            });
                            $('.widget-21a').removeClass('widget-loader-show');
                            $('.widget-21b').removeClass('widget-data-hide');
                        })
                    }

                    self.fte_graphs = function(final_work, type, name) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        if (name == undefined) {
                            name = ''
                        }

                        self.type = type;

                        if ((self.fte_list.length == 1) || (type == 'week') || (type == 'month') || (self.button_clicked == "day_yes")) {

                        var fte_graphs = '/api/fte_graphs/'+self.data_to_show + type + final_work + '&chart_name=11&chart_name=12';

                        return $http({method:"GET", url: fte_graphs}).success(function(result){
    
                            if (type == 'day' && final_work == '') {
                                if (result.result.type == 'day') {
                                    $('.day2').addClass('active btn-success');
                                    $('.day2').siblings().removeClass('active btn-success');
                                    $('.day').addClass('active btn-success');
                                    $('.day').siblings().removeClass('active btn-success');
                                }
                               
                                if (result.result.type == 'week') {
                                    $('.week2').addClass('active btn-success');
                                    $('.week2').siblings().removeClass('active btn-success');
                                    $('.week').addClass('active btn-success');
                                    $('.week').siblings().removeClass('active btn-success');
                                }

                                if (result.result.type == 'month') {
                                    $('.month2').addClass('active btn-success');
                                    $('.month2').siblings().removeClass('active btn-success');
                                    $('.month').addClass('active btn-success');
                                    $('.month').siblings().removeClass('active btn-success');
                                }
                            }
                            var date_list = result.result.date;
                            var work_packet_fte = result.result.fte_calc_data.fte_scope;
                            var total_fte = result.result.fte_calc_data.fte_trend;
                            var is_annotation = result.result.is_annotation;
                            
                            if ((name == "self.chartOptions16") || (name == "")) {

                                if (self.list_object.total_fte != undefined) {
                            
                                    if (self.list_object.total_fte.display_value === true) { 

                                        var value = true;   
                                    }
                                    else {
                                        var value = false;
                                    }
                                }
                                else {
                                    var value = false;
                                }
                                 
                                if (self.list_object.total_fte != undefined) {

                                    if(self.list_object.total_fte.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.total_fte.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }

                                angular.extend(self.chartOptions16, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                                    plotOptions: {
                                        series: {
                                            label: {
                                                connectorAllowed: false
                                            },
                                        dataLabels: {
                                            enabled: value,
                                            valueDecimals: 2
                                        },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {
                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '11<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions16.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            },
                                            events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._fte_data;
                                                    self._data.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-11a').children(".widget-11b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._fte_data;
                                                    self._data.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });                                                    
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-11a').children(".widget-11b").find('.annotation-marker[seies-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    series: work_packet_fte,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self._data = [];
                                    self._fte_data = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=11&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("11", $(self.chartOptions16.chart.renderTo),
                                        chart, point, annotation);
                                   self._data.push(a);
                                   self._fte_data.push(series.name);
                                   window.data = a;
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                  }  
                                });
                                $('.widget-11a').removeClass('widget-loader-show');
                                $('.widget-11b').removeClass('widget-data-hide');
                            }

                            if ((name == "self.chartOptions16_2") || (name == "")) {

                                if (self.list_object.sum_total_fte != undefined) {

                                    if (self.list_object.sum_total_fte.display_value === true) {

                                        var value = true;   
                                    }
                                    else {
                                        var value = false;
                                    }
                                }
                                else {
                                    var value = false;
                                }

                            if (self.list_object.sum_total_fte != undefined) {

                                if(self.list_object.sum_total_fte.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.sum_total_fte.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }
                                angular.extend(self.chartOptions16_2, {
                                    xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                                    plotOptions: {
                                        series: {
                                        dataLabels: {
                                            enabled: value,
                                            valueDecimals: 2
                                        },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{ 
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '12<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions16_2.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }  
                                                }
                                            }
                                        }
                                    },
                                    series: total_fte,
                                    onComplete: function(chart){
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                                          self.type+'&chart_name=12&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];
                                 if(annotation.epoch){
                                   var a = new Annotation("12", $(self.chartOptions16_2.chart.renderTo),
                                        chart, point, annotation);
                                   if(annotation.text == 'undefined') {
                                    $('.arrow').hide();
                                   }
                                   self.annot_perm();  
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                });
                                $('.widget-12a').removeClass('widget-loader-show');
                                $('.widget-12b').removeClass('widget-data-hide');
                          }
                       })
                      }
                    }

                    self.main_prod = function(final_work, type, name) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        if (name == undefined) {
                            name = ''
                        }

                        self.type = type;

                        if ((self.prod_list.length == 1) || (type == 'week') || (type == 'month') || (self.button_clicked == "day_yes")) {

                        var main_prod = '/api/main_prod/'+self.data_to_show + type + final_work + '&chart_name=1&chart_name=6';

                        return $http({method:"GET", url: main_prod}).success(function(result){
            
                            if (type == 'day' && final_work == '') {
                                if (result.result.type == 'day') {
                                    $('.day2').addClass('active btn-success');
                                    $('.day2').siblings().removeClass('active btn-success');
                                    $('.day').addClass('active btn-success');
                                    $('.day').siblings().removeClass('active btn-success');
                                }
                               
                                if (result.result.type == 'week') {
                                    $('.week2').addClass('active btn-success');
                                    $('.week2').siblings().removeClass('active btn-success');
                                    $('.week').addClass('active btn-success');
                                    $('.week').siblings().removeClass('active btn-success');
                                }

                                if (result.result.type == 'month') {
                                    $('.month2').addClass('active btn-success');
                                    $('.month2').siblings().removeClass('active btn-success');
                                    $('.month').addClass('active btn-success');
                                    $('.month').siblings().removeClass('active btn-success');
                                }
                            }
                            var date_list = result.result.date;
                            var main_prod_data = result.result.productivity_data;
                            var is_annotation = result.result.is_annotation;
                            
                            if ((name == "self.chartOptions10") || (name == "")) {
                                                                
                                if (self.list_object.productivity_bar_graph != undefined) {
                                
                                    if (self.list_object.productivity_bar_graph.display_value === true) {

                                        var value = true;
                                    }
                                    else {
                                        var value = false;
                                    }
                                }
                                else {
                                    var value = false;
                                }
                                if (self.list_object.productivity_bar_graph != undefined) {

                                    if(self.list_object.productivity_bar_graph.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                        var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.productivity_bar_graph.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }


                                angular.extend(self.chartOptions10, {
                                   chart:{
                                        type:'column',                                        
                                   },
                                   xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {                                        
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },                                    
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                            formatter: function () {
                                                return Highcharts.numberFormat(this.y, null, null, ",");
                                            },
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: { 
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '6<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions10.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            },
                                            events: {
                                                hide: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._main_prod;
                                                    if (self._value) {
                                                      if (chart_name.indexOf(name) >= 0) {
                                                        self._value.forEach(function(value_data){
                                                          value_data.redraw(name, visibility);
                                                          $(document).find('.widget-6a').children(".widget-6b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                        });                                                                                                  
                                                      }
                                                    }
                                                },
                                                show: function() {
                                                    var name = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._main_prod;
                                                    if (self._value) {
                                                      if (chart_name.indexOf(name) >= 0) {
                                                        self._value.forEach(function(value_data){
                                                          value_data.redraw(name, visibility);
                                                          $(document).find('.widget-6a').children(".widget-6b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                        });                                                                                                                                                                    
                                                      }
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    series: main_prod_data,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self._value = [];
                                    self._main_prod = [];
                                    for(var i in chart_data){  
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=6&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("6", $(self.chartOptions10.chart.renderTo),
                                        chart, point, annotation);
                                   self._value.push(a);
                                   window.value = a;
                                   self._main_prod.push(series.name);
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                  }
                                });
                                $('.widget-6a').removeClass('widget-loader-show');
                                $('.widget-6b').removeClass('widget-data-hide');
                            }

                            if ((name == "self.chartOptions") || (name == "")) {

                                if (self.list_object.productivity_chart != undefined) {

                                    if (self.list_object.productivity_chart.display_value === true) {

                                        var value = true;
                                    }
                                    else {
                                        var value = false;
                                    }
                                }
                                else {
                                    var value = false;
                                }

                                if (self.list_object.productivity_chart != undefined) {

                                    if(self.list_object.productivity_chart.legends_align == 'bottom') {
                                    
                                        var align = 'center';
                                       var ver_align = 'bottom';
                                        var layout = 'horizontal';
                                
                                    }
                                
                                    else if(self.list_object.productivity_chart.legends_align == 'left'){
                                
                                        var align ='left';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                
                                    else {
                                        var align = 'right';
                                        var ver_align = 'top';
                                        var layout = 'vertical';
                                    }
                                }
                                
                                else {
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                                }

                                angular.extend(self.chartOptions, {
                                   xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },
                            
                                    plotOptions: {
                                        series: {
                                            dataLabels: {
                                                enabled: value,
                                                formatter: function () {
                                                    return Highcharts.numberFormat(this.y, null, null, ",");
                                                },
                                            },
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                           events:{ 
                                            contextmenu: function() {
                                                if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                }
                                                else {
                                                    if (self.data_to_show.split('&').length == 6) {
                                                        var sub_proj = '';
                                                        var work_pack = '';
                                                        var sub_pack = '';
                                                    }
                                                    else {
                                                        var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                        var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                        var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                    }
                                                    var str = '1<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                            this['project'] = self.project_live;
                                                            this['center'] = self.center_live;
                                                            this['from'] = self.start_date;
                                                            this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions.chart.renderTo),this.series.chart, this);
                                                }
                                            } 
                                            }
                                         },
                                         events: {
                                                hide: function() {
                                                      var name = this.name;
                                                      var visibility = this.visible;
                                                      var chart_name = self._main_prod_line;
                                                      if (self.anno_data) {
                                                        if (chart_name.indexOf(name) >= 0) {
                                                          self.anno_data.forEach(function(value_data){
                                                              value_data.redraw(name, visibility);
                                                              $(document).find('.widget-1a').children(".widget-1b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                          });                                                                                                          
                                                        }
                                                      }
                                                },
                                                show: function() {    
                                                      var name = this.name;
                                                      var visibility = this.visible;
                                                      var chart_name = self._main_prod_line;
                                                      if (self.anno_data) {
                                                        if (chart_name.indexOf(name) >= 0) {
                                                          self.anno_data.forEach(function(value_data){
                                                            value_data.redraw(name, visibility);
                                                            $(document).find('.widget-1a').children(".widget-1b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                          });                                                                                                              
                                                        }
                                                      }
                                                }
                                            }
                                        }
                                    },

                                    series: main_prod_data,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self.anno_data = [];
                                    self._main_prod_line = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=1&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){  
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("1", $(self.chartOptions.chart.renderTo),
                                        chart, point, annotation);
                                   self.anno_data.push(a);
                                   window.anno_data = a;
                                   self._main_prod_line.push(series.name);
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                  }  
                                });     
                                $('.widget-1a').removeClass('widget-loader-show');
                                $('.widget-1b').removeClass('widget-data-hide');
                           }  
                        })
                      }  
                    }
        
                    self.category_error = function(cate_error){

                        if (self.cate_pie.length == 1) {
                            return $http({method:"GET", url: cate_error }).success(function(result){

                                angular.extend(self.chartOptions5,{

                                    series: [{
                                        name: '',
                                        colorByPoint: true,
                                        cursor: 'pointer',
                                        data: result.result.internal_errors_types
                                    }]
                                });
                                $('.widget-4a').removeClass('widget-loader-show');
                                $('.widget-4b').removeClass('widget-data-hide');

                                angular.extend(self.chartOptions5_2,{
                                    series: [{
                                        name: '',
                                        colorByPoint: true,
                                        cursor: 'pointer',
                                        data: result.result.external_errors_types
                                    }]
                                });
                                $('.widget-5a').removeClass('widget-loader-show');
                                $('.widget-5b').removeClass('widget-data-hide');
                            })
                        }
                    }

        self.pareto_category_error = function(pareto_cate_error){

                       if (self.cate_pareto.length == 1) {

                       return $http({method:"GET", url: pareto_cate_error + '&chart_name=24&chart_name=25' }).success(function(result){
                            var is_annotation = result.result.is_annotation;
                            if (self.list_object.error_category_internal_pareto_analysis != undefined) {

                                if (self.list_object.error_category_internal_pareto_analysis.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }
    
                            angular.extend(self.chartOptions29, {
                                xAxis: {
                                    categories: result.result.internal_error_category.category_name,
                                title: {
                                    text: '',
                                 }
                               },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '24<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions29.chart.renderTo),this.series.chart, this);
                                                }
                                            }
                                           } 
                                        },
                                        events: {
                                            hide: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-24a').find('.annotation-marker[series-name="'+this.name+'"]').hide();
                                            },
                                            show: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-24a').find('.annotation-marker[series-name="'+this.name+'"]').show();
                                            }
                                        }
                                    }
                                },
    
                               series: result.result.internal_error_category.category_pareto,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                          self.type+'&chart_name=24&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("24", $(self.chartOptions29.chart.renderTo),
                                        chart, point, annotation);
                                   window.annotObj = a;
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                }
                            });
                            $('.widget-24a').removeClass('widget-loader-show');
                            $('.widget-24b').removeClass('widget-data-hide');

                            if (self.list_object.error_category_external_pareto_analysis != undefined) {

                                if (self.list_object.error_category_external_pareto_analysis.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                            angular.extend(self.chartOptions30, {
                                xAxis: {
                                    categories: result.result.external_error_category.category_name,
                                title: {
                                    text: '',
                                 }
                               },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                       point: {
                                          events:{
                                            contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                              if (self.data_to_show.split('&').length == 6) { 
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '25<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions30.chart.renderTo),this.series.chart, this);
                                                }
                                               } 
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-25a').find('.annotation-marker[series-name="'+this.name+'"]').hide();
                                            },
                                            show: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-25a').find('.annotation-marker[series-name="'+this.name+'"]').show();
                                            }
                                        }
                                    }
                                },                            
                               series: result.result.external_error_category.category_pareto,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=25&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("25", $(self.chartOptions30.chart.renderTo),
                                        chart, point, annotation);
                                   window.annotObj = a;
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                 }   
                            });
                            $('.widget-25a').removeClass('widget-loader-show');
                            $('.widget-25b').removeClass('widget-data-hide');
                       })
                 }
           }
          
        self.agent_category_error = function(agent_cate_error){
                        
                       if (self.agent_pareto.length == 1) {
                       return $http({method:"GET", url: agent_cate_error + '&chart_name=22&chart_name=23' }).success(function(result){
                            var is_annotation = result.result.is_annotation;
                            if (self.list_object.agent_wise_pareto_graph_data != undefined) {

                                if (self.list_object.agent_wise_pareto_graph_data.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }
    
                            angular.extend(self.chartOptions27, {
                                xAxis: {
                                    categories: result.result.pareto_data.category_name,
                                title: {
                                    text: '',
                                 }
                               },

                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                          enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '22<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions27.chart.renderTo),this.series.chart, this);
                                                }
                                              }
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-22a').find('.annotation-marker[series-name="'+this.name+'"]').hide();
                                            },
                                            show: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-22a').find('.annotation-marker[series-name="'+this.name+'"]').show();
                                            }
                                        }
                                    }
                                },
                               series: result.result.pareto_data.category_pareto,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                          self.type+'&chart_name=22&project='+self.project_live+'&center='+
                          self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("22", $(self.chartOptions27.chart.renderTo),
                                        chart, point, annotation);
                                   window.annotObj = a;
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                }
                            });
                            $('.widget-22a').removeClass('widget-loader-show');
                            $('.widget-22b').removeClass('widget-data-hide');

                           if (self.list_object.agent_wise_external_pareto_analysis != undefined) {

                                if (self.list_object.agent_wise_external_pareto_analysis.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                            angular.extend(self.chartOptions28, {
                                xAxis: {
                                    categories: result.result.external_pareto_data.category_name,
                                title: {
                                    text: '',
                                 }
                               },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '23<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions28.chart.renderTo),this.series.chart, this);
                                                }
                                              }
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-23a').find('.annotation-marker[series-name="'+this.name+'"]').hide();
                                            },
                                            show: function() {
                                                window.annotObj.redraw(this.name, this.visible);
                                                $(document).find('.widget-23a').find('.annotation-marker[series-name="'+this.name+'"]').show();
                                            }
                                        }
                                    }
                                },

                               series: result.result.external_pareto_data.category_pareto,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=23&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){ 
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("23", $(self.chartOptions28.chart.renderTo),
                                        chart, point, annotation);
                                   window.annotObj = a;
                                   self.annot_perm();
                                   }
                               })
                                        });
                                        }(series));
                                    }
                                    }
                                }
                            });
                            $('.widget-23a').removeClass('widget-loader-show');
                            $('.widget-23b').removeClass('widget-data-hide');
                       }) 
                }
         }

                    self.performance = function(final_work,type,date_key){
                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }
                        
                        if (date_key == undefined){
                            var performance_summary = '/api/performance_summary/'+self.data_to_show + type + final_work;
                        }
                        else{
                            date_key = date_key.split('@')
                            var performance_summary = '/api/performance_summary/'+self.data_to_show + type + final_work+"&key_from_date="+date_key[0]+"&key_to_date="+date_key[1];   
                        }

                        
                        self.type = type;

                        
                        return $http({method:"GET", url: performance_summary + '&chart_name=64' }).success(function(result){

                            $('.widget-62a').addClass('widget-loader-show');
                            $('.widget-62b').addClass('widget-data-hide');
                            $("#widget-62a-jumio").remove();
                            var res = result["result"]
                            var predate_list = res["previous_date"][0]+"@"+res["previous_date"][res["previous_date"].length - 1]
                            var predate = res["previous_date"][0].split("-").slice(1,3).toString().replace(","," - ") + ' To '+ res["previous_date"][res["previous_date"].length - 1].split("-").slice(1,3).toString().replace(","," - ");
                            var curdate = res["current_date"][0].split("-").slice(1,3).toString().replace(","," - ") + ' To '+ res["current_date"][res["current_date"].length - 1].split("-").slice(1,3).toString().replace(","," - ");
                            // var table_html = "<table id='widget-62a-jumio' class='table table-responsive table table-condensed table-striped table-bordered' style='text-align-last: center;'><thead><tr><th colspan='9'></th><th>Total</th><th  colspan='2'>Average</th><tr>";
                            var table_html = "<div id='widget-62a-jumio' class='table-responsive-sm' ><table class='table table-condensed' style='text-align-last: center;'><thead><tr class='success'><th colspan='9'></th><th>Total</th><th  colspan='2'>Average</th><tr class='success'>";
                            table_html = table_html +"<th>Date</th><th><a data-toggle='tooltip' title='Previous Week' ng-click=$ctrl.performance(undefined,undefined,'"+predate_list+"')>"+predate+"</a></th>";
                            var production_count = "<tr><td class='info'>Production Count</td><td class='success'>"+res['pre_main_result']['Pre_Production_Count']+"</td>";
                            var Audit_Count = "<tr><td class='info'>Audit Count</td><td class='success'>"+res['pre_main_result']['Pre_Audit_Count']+"</td>";
                            var Error_Count = "<tr><td class='info'>Error Count</td><td class='success'>"+res['pre_main_result']['Pre_Error_Count']+"</td>";
                            var Accuracy = "<tr><td class='info'>Accuracy %</td><td class='success'>"+res['pre_main_result']['Pre_Accuracy']+"</td>";
                            var AHT_Avg = "<tr><td class='info'>AHT Avg</td><td class='success'>"+res['pre_main_result']['Pre_Aht_Avg']+"</td>";
                            var No_of_Logins = "<tr><td class='info'>No of Logins</td><td class='success'>"+res['pre_main_result']['Pre_login_count']+"</td>";
                            var prod_count = 0;
                            var aud_count = 0;
                            var err_count = 0;
                            var acc_count = 0;
                            var aht_count = 0;
                            var login_count = 0;
                            var counter_var = [0,0,0,0,0,0]

                            for (var ij =0;ij < res["current_date"].length;ij++){
                                 table_html = table_html + "<th>"+res['current_date'][ij]+"</th>";
                                 
                                 if (res['production'][res['current_date'][ij]]){
                                    production_count = production_count + "<td class='info'>" +res['production'][res['current_date'][ij]] +"</td>" 
                                    prod_count = prod_count + res['production'][res['current_date'][ij]]
                                    counter_var[0]++;
                                 }
                                 else{
                                    production_count = production_count + "<td class='info'> NA </td>" 
                                 }

                                 if (res['audit_count'][res['current_date'][ij]]){
                                    Audit_Count = Audit_Count + "<td class='info'>" +res['audit_count'][res['current_date'][ij]] +"</td>" 
                                    aud_count = aud_count + res['audit_count'][res['current_date'][ij]]
                                    counter_var[1]++;
                                 }
                                 else{
                                    Audit_Count = Audit_Count + "<td class='info'> NA </td>" 
                                 }
                                 
                                 if(res['audit_errors'][res['current_date'][ij]]){
                                    Error_Count = Error_Count + "<td class='info'>" +res['audit_errors'][res['current_date'][ij]] +"</td>" 
                                    err_count = err_count + res['audit_errors'][res['current_date'][ij]]
                                    counter_var[2]++;
                                 }
                                 else{
                                    Error_Count = Error_Count + "<td class='info'> NA </td>" 
                                 }
                                 
                                 if(res['accuracy'][res['current_date'][ij]]){
                                    Accuracy = Accuracy + "<td class='info'>" +res['accuracy'][res['current_date'][ij]] +"% </td>" 
                                    acc_count = acc_count + res['accuracy'][res['current_date'][ij]]
                                    counter_var[3]++;
                                 }
                                 else{
                                    
                                    Accuracy = Accuracy + "<td class='info'> NA </td>" 
                                 }
                                 
                                 if(res['AHT_avg'][res['current_date'][ij]]){
                                    AHT_Avg = AHT_Avg + "<td class='info'>" +res['AHT_avg'][res['current_date'][ij]] +"</td>" 
                                    aht_count = aht_count + res['AHT_avg'][res['current_date'][ij]]
                                    counter_var[4]++;
                                 }
                                 else{
                                    AHT_Avg = AHT_Avg + "<td class='info'> NA </td>" 
                                 }
                                                                  
                                 if(res['AHT_count'][res['current_date'][ij]] != undefined){
                                    No_of_Logins = No_of_Logins + "<td class='info'>" +res['AHT_count'][res['current_date'][ij]] +"</td>" 
                                    login_count = login_count + res['AHT_count'][res['current_date'][ij]]
                                    counter_var[5]++;
                                 }
                                 else{
                                    No_of_Logins = No_of_Logins + "<td class='info'> NA </td>" 
                                 }
                            }
                            
                            if (counter_var[0] >0) {
                                production_count = production_count + '<td class="success">'+prod_count+'</td><td class="success">'+res["pre_main_result"]["Pre_Production_Count"]+'</td><td class="success">'+(prod_count/counter_var[0]).toFixed(0)+'</td></tr>'
                            }
                            else{
                             production_count = production_count + '<td class="success"> NA </td><td class="success"> NA </td><td class="success"> NA </td></tr>'   
                            }
                            
                            if (counter_var[1] >0){
                                Audit_Count = Audit_Count + '<td class="success">'+aud_count+'</td><td class="success">'+res["pre_main_result"]["Pre_Audit_Count"]+'</td><td class="success">'+(aud_count)+'</td></tr>'    
                            }
                            else{
                                Audit_Count = Audit_Count + '<td class="success"> NA </td><td class="success">'+res["pre_main_result"]["Pre_Audit_Count"]+'</td><td class="success"> NA </td></tr>'
                            }
                            
                            if(counter_var[2] > 0){
                                Error_Count = Error_Count + '<td class="success">'+err_count+'</td><td class="success">'+res["pre_main_result"]["Pre_Error_Count"]+'</td><td class="success">'+(err_count)+'</td></tr>'
                            }
                            else{
                                Error_Count = Error_Count + '<td class="success"> NA </td><td class="success">'+res["pre_main_result"]["Pre_Error_Count"]+'</td><td class="success"> NA </td></tr>'
                            }
                            
                            if(counter_var[3] > 0){
                                Accuracy = Accuracy + '<td class="success">'+(acc_count / counter_var[3]).toFixed(2)+'% </td><td class="success">'+res["pre_main_result"]["Pre_Accuracy"]+'</td><td class="success">'+(acc_count/counter_var[3]).toFixed(2)+'% </td></tr>'
                            }
                            else{
                                Accuracy = Accuracy + '<td class="success"> NA </td><td class="success">'+res["pre_main_result"]["Pre_Accuracy"]+'</td><td class="success"> NA </td></tr>'
                            }

                            if (counter_var[4] > 0){
                                AHT_Avg = AHT_Avg + '<td class="success">'+(aht_count/counter_var[4]).toFixed(2)+'</td><td class="success">'+res["pre_main_result"]["Pre_Aht_Avg"]+'</td><td class="success">'+(aht_count/counter_var[4]).toFixed(2)+'</td></tr>'    
                            }
                            else{
                                AHT_Avg = AHT_Avg + '<td class="success"> NA </td><td class="success">'+res["pre_main_result"]["Pre_Aht_Avg"]+'</td><td class="success"> NA </td></tr>'
                            }

                            if(counter_var[5] > 0){
                                No_of_Logins = No_of_Logins + '<td class="success">'+(login_count/counter_var[5]).toFixed(0)+'</td><td class="success">'+res["pre_main_result"]["Pre_login_count"]+'</td><td class="success">'+(login_count/counter_var[5]).toFixed(0)+'</td></tr>'
                            }
                            else{
                                No_of_Logins = No_of_Logins + '<td class="success"> NA </td><td class="success">'+res["pre_main_result"]["Pre_login_count"]+'</td><td class="success"> NA </td></tr>'
                            }
                            

                            table_html = table_html + '<th>'+ curdate +'</th><th>'+ predate +'</th><th>'+ curdate +'</th></tr></thead><tbody class="info">';
                            

                            table_html = table_html + production_count + Audit_Count + Error_Count + Accuracy + AHT_Avg + No_of_Logins + "</tbody></table></div>";
                            $(".widget-62b highcharts").remove()
                            $('.widget-62b').css('overflow','auto');
                            var $el = $(table_html).appendTo(".widget-body.widget-62b");
                            $compile($el)($scope);


                            
                            $('.widget-62a').removeClass('widget-loader-show');
                            $('.widget-62b').removeClass('widget-data-hide');
                        });
                    }

  function isEmpty(obj){
    for (var key in obj){
      if(obj.hasOwnProperty(key)){
        return false;
      }
    }
    return true;
  }

  function* enumerate(obj){
    var i =0;
    for (var key in obj){
      yield [i, key];
      i++;
    }
  }


  self.static_internal_external_agent_errors= function(){
    var error_data = '/api/static_internal_external_agent_errors/?'+self.static_widget_data;
    return $http({method:"GET", url: error_data }).success(function(result){
      if(isEmpty(result['result'].thirty_days_data.internalerrors)&&isEmpty(result['result'].sixty_days_data.internalerrors)&&isEmpty(result['result'].ninty_days_data.internalerrors)){
        var table_html = '<div style="font-size:11px; color:#5b5b5b; font-weight:bold;display:flex; justify-content:center; margin-top:100px"><p>No data to display</p></div>';
        $(".widget-66b highcharts").remove();
        $('.widget-66b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-66b");
        $compile($el)($scope);
        $('.widget-66a').removeClass('widget-loader-show');
        $('.widget-66b').removeClass('widget-data-hide');

      }else{
        $('.widget-66a').addClass('widget-oader-show');
        $('.widget-66b').addClass('widget-data-hide');
        $("#widget-66-agent-error").remove();
        var thirty_days_internal_agent_data = result['result'].thirty_days_data.internalerrors;
        var sixty_days_internal_agent_data = result['result'].sixty_days_data.internalerrors;
        var ninty_days_internal_agent_data = result['result'].ninty_days_data.internalerrors;

        var widget = "<div id='widget-66-agent-error' style='margin-top:20px; display:flex; justify-content:center'>";
        var card_html_1 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_2 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_3 = "<div class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var cards = [card_html_1, card_html_2, card_html_3];
        var total_agent_errors = [thirty_days_internal_agent_data, sixty_days_internal_agent_data, ninty_days_internal_agent_data];

        for(var k = 0; k<total_agent_errors.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_agent_errors[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_agent_errors[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards[k]+=rows[i];
          cards[k]+="</div>";
        }

        card_html_1=cards[0]+"</div>";
        card_html_2=cards[1]+"</div>";
        card_html_3=cards[2]+"</div>";
        widget+=card_html_1+card_html_2+card_html_3+"</div>";

        $(".widget-66b highcharts").remove();
        $('.widget-66b').css('overflow','auto');
        var $el = $(widget).appendTo(".widget-body.widget-66b");
        $compile($el)($scope);
        $('.widget-66a').removeClass('widget-loader-show');
        $('.widget-66b').removeClass('widget-data-hide');
      }
      // ===================For External Errors =========================

      if(isEmpty(result['result'].thirty_days_data.externalerrors)&&isEmpty(result['result'].sixty_days_data.externalerrors)&&isEmpty(result['result'].ninty_days_data.externalerrors)){
        var table_html= '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-67b highcharts").remove();
        $('.widget-67b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-67b");
        $compile($el)($scope);
        $('.widget-67a').removeClass('widget-loader-show');
        $('.widget-67b').removeClass('widget-data-hide');

      }else{
        $('.widget-67a').addClass('widget-loader-show');
        $('.widget-67b').addClass('widget-data-hide');
        $("#widget-67-agent-error").remove();
        var thirty_days_external_agent_data = result['result'].thirty_days_data.externalerrors;
        var sixty_days_external_agent_data = result['result'].sixty_days_data.externalerrors;
        var ninty_days_external_agent_data = result['result'].ninty_days_data.externalerrors;

        var widget_2 = "<div id='widget-67-agent-error' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_4 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_5 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_6 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var total_agent_errors = [thirty_days_external_agent_data, sixty_days_external_agent_data, ninty_days_external_agent_data];

        var cards_2 = [card_html_4, card_html_5, card_html_6];
        for(var k = 0; k<total_agent_errors.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_agent_errors[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_agent_errors[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards_2[k]+=rows[i];
          cards_2[k]+="</div>";
        }

        card_html_4=cards_2[0]+"</div>";
        card_html_5=cards_2[1]+"</div>";
        card_html_6=cards_2[2]+"</div>";
        widget_2+=card_html_4+card_html_5+card_html_6+"</div>";
        $(".widget-67b highcharts").remove()
        $('.widget-67b').css('overflow','auto');
        var $el = $(widget_2).appendTo(".widget-body.widget-67b");
        $compile($el)($scope);

        $('.widget-67a').removeClass('widget-loader-show');
        $('.widget-67b').removeClass('widget-data-hide');

      }
    });
  };


  self.static_internal_external_error_category = function(){
    var error_category = '/api/static_internal_external_error_category/?'+self.static_widget_data;
    return $http({method:"GET", url: error_category }).success(function(result){
      if(isEmpty(result['result'].thirty_days_data.internalerrors) && isEmpty(result['result'].sixty_days_data.internalerrors)&& isEmpty(result['result'].ninty_days_data.internalerrors)){
        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-68b highcharts").remove();
        $('.widget-68b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-68b");
        $compile($el)($scope);
        $('.widget-68a').removeClass('widget-loader-show');
        $('.widget-68b').removeClass('widget-data-hide');

      }else{
        $('.widget-68a').addClass('widget-loader-show');
        $('.widget-68b').addClass('widget-data-hide');

        $("#widget-68-error-category").remove();
        var thirty_days_internal_error_category = result['result'].thirty_days_data.internalerrors;
        var sixty_days_internal_error_category = result['result'].sixty_days_data.internalerrors;
        var ninty_days_internal_error_category = result['result'].ninty_days_data.internalerrors;

        var widget = "<div id='widget-68-error-category' style='display:flex; justify-content:center'>";
        var card_html_1 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_2 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_3 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var rows = ['', '', '', '', ''];
        var total_category_errors = [thirty_days_internal_error_category, sixty_days_internal_error_category, ninty_days_internal_error_category];

        var cards = [card_html_1, card_html_2, card_html_3];
        for(var k = 0; k < total_category_errors.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_category_errors[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_category_errors[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards[k]+=rows[i];
          cards[k]+="</div>";
        }

        card_html_1=cards[0]+"</div>";
        card_html_2=cards[1]+"</div>";
        card_html_3=cards[2]+"</div>";
        widget+=card_html_1+card_html_2+card_html_3+"</div>";

        $(".widget-68b highcharts").remove();
        $('.widget-68b').css('overflow','auto');
        var $el = $(widget).appendTo(".widget-body.widget-68b");

        $compile($el)($scope);
        $('.widget-68a').removeClass('widget-loader-show');
        $('.widget-68b').removeClass('widget-data-hide');
      }

     // ===================For External Errors =========================

      if(isEmpty(result['result'].thirty_days_data.externalerrors)&&isEmpty(result['result'].sixty_days_data.externalerrors)&&isEmpty(result['result'].ninty_days_data.externalerrors)){

        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-69b highcharts").remove();
        $('.widget-69b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-69b");
        $compile($el)($scope);
        $('.widget-69a').removeClass('widget-loader-show');
        $('.widget-69b').removeClass('widget-data-hide');
      }else{
        $('.widget-69a').addClass('widget-loader-show');
        $('.widget-69b').addClass('widget-data-hide');
        $("#widget-69-error-category").remove();

        var thirty_days_external_error_category = result['result'].thirty_days_data.externalerrors;
        var sixty_days_external_error_category = result['result'].sixty_days_data.externalerrors;
        var ninty_days_external_error_category = result['result'].ninty_days_data.externalerrors;

        var widget_2 = "<div id='widget-69-error-category' style='display:flex; justify-content:center;'>";

        var card_html_4 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_5 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_6 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var cards_2 = [card_html_4, card_html_5, card_html_6];

        var total_category_errors = [thirty_days_external_error_category, sixty_days_external_error_category, ninty_days_external_error_category];

        for(var k = 0; k < total_category_errors.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_category_errors[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_category_errors[k][key]+"</p></div>";
          }
          for(var i =0; i<rows.length; i++)
            cards_2[k]+=rows[i];
          cards_2[k]+="</div>";
        }

        card_html_4=cards_2[0]+"</div>";
        card_html_5=cards_2[1]+"</div>";
        card_html_6=cards_2[2]+"</div>";

        widget_2+=card_html_4+card_html_5+card_html_6+"</div>";

        $(".widget-69b highcharts").remove()
        $('.widget-69b').css('overflow','auto');
        var $el = $(widget_2).appendTo(".widget-body.widget-69b");
        $compile($el)($scope);

        $('.widget-69a').removeClass('widget-loader-show');
        $('.widget-69b').removeClass('widget-data-hide');

      }
    });
  };

  self.static_internal_external_packet_errors = function() {
    var error_data = '/api/static_internal_external_packet_errors/?'+self.static_widget_data
    return $http({method:"GET", url: error_data }).success(function(result){
      if(isEmpty(result['result'].thirty_days_data.internalerrors)&&isEmpty(result['result'].sixty_days_data.internalerrors)&&isEmpty(result['result'].ninty_days_data.internalerrors)){

        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-70b highcharts").remove();
        $('.widget-70b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-70b");
        $compile($el)($scope);
        $('.widget-70a').removeClass('widget-loader-show');
        $('.widget-70b').removeClass('widget-data-hide');
      }else{
        $('.widget-70a').addClass('widget-loader-show');
        $('.widget-70b').addClass('widget-data-hide');
        $("#widget-70-packet-wise-error").remove();
        var thirty_days_packet_wise_data = result['result'].thirty_days_data.internalerrors;
        var sixty_days_packet_wise_data = result['result'].sixty_days_data.internalerrors;
        var ninty_days_packet_wise_data = result['result'].ninty_days_data.internalerrors;

        var widget = "<div id='widget-70-packet-wise-error' style='margin-top:20px; display:flex;justify-content:center'>";
        var card_html_1 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";
        var card_html_2 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";
        var card_html_3 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";
        var cards = [card_html_1, card_html_2, card_html_3];

        var total_packet_wise_errors = [thirty_days_packet_wise_data, sixty_days_packet_wise_data, ninty_days_packet_wise_data];

        for(var k = 0; k < total_packet_wise_errors.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_packet_wise_errors[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_packet_wise_errors[k][key]+"</p></div>";
          }
          for(var i =0; i<rows.length; i++)
            cards[k]+=rows[i];
          cards[k]+="</div>";
        }

        card_html_1=cards[0]+"</div>";
        card_html_2=cards[1]+"</div>";
        card_html_3=cards[2]+"</div>";
        widget+=card_html_1+card_html_2+card_html_3+"</div>";

        $(".widget-70b highcharts").remove();
        $('.widget-70b').css('overflow','auto');
        var $el = $(widget).appendTo(".widget-body.widget-70b");

        $compile($el)($scope);

        $('.widget-70a').removeClass('widget-loader-show');
        $('.widget-70b').removeClass('widget-data-hide');
      }

      // For external packets

      if(isEmpty(result['result'].thirty_days_data.externalerrors) && isEmpty(result['result'].sixty_days_data.externalerrors)&& isEmpty(result['result'].ninty_days_data.externalerrors)){
        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-71b highcharts").remove();
        $('.widget-71b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-71b");
        $compile($el)($scope);
        $('.widget-71a').removeClass('widget-loader-show');
        $('.widget-71b').removeClass('widget-data-hide');
      }else{
        $('.widget-71a').addClass('widget-loader-show');
        $('.widget-71b').addClass('widget-data-hide');
        $("#widget-71-packet-wise-error").remove();
        var thirty_days_packet_wise_data = result['result'].thirty_days_data.externalerrors;
        var sixty_days_packet_wise_data = result['result'].sixty_days_data.externalerrors;
        var ninty_days_packet_wise_data = result['result'].ninty_days_data.externalerrors;

        var widget_2 = "<div id='widget-71-packet-wise-error' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_4 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";
        var card_html_5 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";
        var card_html_6 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";
        var cards_2 = [card_html_4, card_html_5, card_html_6];

        var total_packet_wise_errors = [thirty_days_packet_wise_data, sixty_days_packet_wise_data, ninty_days_packet_wise_data];

        for(var k = 0; k < total_packet_wise_errors.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_packet_wise_errors[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_packet_wise_errors[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards_2[k]+=rows[i];
          cards_2[k]+="</div>";
        }

        card_html_4=cards_2[0]+"</div>";
        card_html_5=cards_2[1]+"</div>";
        card_html_6=cards_2[2]+"</div>";

        widget_2+=card_html_4+card_html_5+card_html_6+"</div>";

        $(".widget-71b highcharts").remove();
        $('.widget-71b').css('overflow','auto');
        var $el = $(widget_2).appendTo(".widget-body.widget-71b");
        $compile($el)($scope);
        $('.widget-71a').removeClass('widget-loader-show');
        $('.widget-71b').removeClass('widget-data-hide');
      }
    });
  };

  self.static_internal_external_packet_accuracy = function(){
    var url = '/api/static_internal_external_packet_accuracy/?'+self.static_widget_data;
    return $http({'method':'GET', 'url':url}).success(function(result){
      if(isEmpty(result['result'].thirty_days_data.internalerrors)&&isEmpty(result['result'].sixty_days_data.internalerrors)&&isEmpty(result['result'].ninty_days_data.internalerrors)){
        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-72b highcharts").remove();
        $('.widget-72b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body .widget-72b");
        $compile($el)($scope);
        $('.widget-72a').removeClass('widget-loader-show');
        $('.widget-72b').removeClass('widget-data-hide');
      }else{
        $('.widget-72a').addClass('widget-loader-show');
        $('.widget-72b').addClass('widget-data-hide');
        $("#widget-72-packet-accuracy").remove();
        var thirty_days_internal_packet_accuracy = result['result'].thirty_days_data.internalerrors;
        var sixty_days_internal_packet_accuracy = result['result'].sixty_days_data.internalerrors;
        var ninty_days_internal_packet_accuracy = result['result'].ninty_days_data.internalerrors;
        var widget = "<div id='widget-72-packet-accuracy' style='margin-top:20px; display:flex; justify-content:center'>";
        var card_html_1 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_2 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_3 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var cards = [card_html_1, card_html_2, card_html_3];
        var total_packet_accuracy = [thirty_days_internal_packet_accuracy, sixty_days_internal_packet_accuracy, ninty_days_internal_packet_accuracy];

        for(var k = 0; k<total_packet_accuracy.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_packet_accuracy[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_packet_accuracy[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards[k]+=rows[i];
          cards[k]+="</div>";
        }

        card_html_1=cards[0]+"</div>";
        card_html_2=cards[1]+"</div>";
        card_html_3=cards[2]+"</div>";
        widget+=card_html_1+card_html_2+card_html_3+"</div>";

        $(".widgt-72b highcharts").remove();
        $('.widget-72b').css('overflow','auto');
        var $el = $(widget).appendTo(".widget-body.widget-72b");
        $compile($el)($scope);
        $('.widget-72a').removeClass('widget-loader-show');
        $('.widget-72b').removeClass('widget-data-hide');
      }

      // ===================For External Errors =========================

      if(isEmpty(result['result'].thirty_days_data.externalerrors)&&isEmpty(result['result'].sixty_days_data.externalerrors)&&isEmpty(result['result'].ninty_days_data.externalerrors)){
        var table_html= '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-73b highcharts").remove();
        $('.widget-73b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-73b");
        $compile($el)($scope);
        $('.widget-73a').removeClass('widget-loader-show');
        $('.widget-73b').removeClass('widget-data-hide');

      }else{
        $('.widget-73a').addClass('widget-loader-show');
        $('.widget-73b').addClass('widget-data-hide');
        $("#widget-73-packet-accuracy").remove();
        var thirty_days_external_packet_accuracy = result['result'].thirty_days_data.externalerrors;
        var sixty_days_external_packet_accuracy = result['result'].sixty_days_data.externalerrors;
        var ninty_days_external_packet_accuracy = result['result'].ninty_days_data.externalerrors;
        var widget_2 = "<div id='widget-73-packet-accuracy' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_4 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_5 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_6 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var total_packet_accuracy = [thirty_days_external_packet_accuracy, sixty_days_external_packet_accuracy, ninty_days_external_packet_accuracy];

        var cards_2 = [card_html_4, card_html_5, card_html_6];
        for(var k = 0; k<total_packet_accuracy.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_packet_accuracy[k])){
            rows[i]+=rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_packet_accuracy[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
              cards_2[k]+=rows[i];
          cards_2[k]+="</div>";
        }

        card_html_4=cards_2[0]+"</div>";
        card_html_5=cards_2[1]+"</div>";
        card_html_6=cards_2[2]+"</div>";
        widget_2+=card_html_4+card_html_5+card_html_6+"</div>";
        $(".widget-73b highcharts").remove()
        $('.widget-73b').css('overflow','auto');
        var $el = $(widget_2).appendTo(".widget-body.widget-73b");
        $compile($el)($scope);

        $('.widget-73a').removeClass('widget-loader-show');
        $('.widget-73b').removeClass('widget-data-hide');

      }
    });
  };

    self.static_internal_external_agent_accuracy = function(){
    var url = '/api/static_internal_external_agent_accuracy/?'+self.static_widget_data;
    return $http({'method':'GET', 'url':url}).success(function(result){
      if(isEmpty(result['result'].thirty_days_data.internalerrors)&&isEmpty(result['result'].sixty_days_data.internalerrors)&&isEmpty(result['result'].ninty_days_data.internalerrors)){
        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold;display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-74b highcharts").remove();
        $('.widget-74b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-74b");
        $compile($el)($scope);
        $('.widget-74a').removeClass('widget-loader-show');
        $('.widget-74b').removeClass('widget-data-hide');

      }else{
        $('.widget-74a').addClass('widget-loader-show');
        $('.widget-74b').addClass('widget-data-hide');
        $("#widget-74-agent-accuracy").remove();
        var thirty_days_internal_agent_accuracy = result['result'].thirty_days_data.internalerrors;
        var sixty_days_internal_agent_accuracy = result['result'].sixty_days_data.internalerrors;
        var ninty_days_internal_agent_accuracy = result['result'].ninty_days_data.internalerrors;
        var widget = "<div id='widget-74-agent-accuracy' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_1 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_2 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_3 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var cards = [card_html_1, card_html_2, card_html_3];
        var total_agent_accuracy = [thirty_days_internal_agent_accuracy, sixty_days_internal_agent_accuracy, ninty_days_internal_agent_accuracy];

        for(var k = 0; k<total_agent_accuracy.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_agent_accuracy[k])){
              rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_agent_accuracy[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards[k]+=rows[i];
          cards[k]+="</div>";
        }

        card_html_1=cards[0]+"</div>";
        card_html_2=cards[1]+"</div>";
        card_html_3=cards[2]+"</div>";
        widget+=card_html_1+card_html_2+card_html_3+"</div>";

        $(".widget-74b highcharts").remove();
        $('.widget-74b').css('overflow','auto');
        var $el = $(widget).appendTo(".widget-body.widget-74b");
        $compile($el)($scope);
        $('.widget-74a').removeClass('widget-loader-show');
        $('.widget-74b').removeClass('widget-data-hide');
      }
      // ===================For External Errors =========================

      if(isEmpty(result['result'].thirty_days_data.externalerrors)&&isEmpty(result['result'].sixty_days_data.externalerrors)&&isEmpty(result['result'].ninty_days_data.externalerrors)){
        var table_html= '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-75b highcharts").remove();
        $('.widget-75b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-75b");
        $compile($el)($scope);
        $('.widget-75a').removeClass('widget-loader-show');
        $('.widget-75b').removeClass('widget-data-hide');

      }else{
        $('.widget-75a').addClass('widget-loader-show');
        $('.widget-75b').addClass('widget-data-hide');
        $("#widget-75-agent-accuracy").remove();
        var thirty_days_external_agent_accuracy = result['result'].thirty_days_data.externalerrors;
        var sixty_days_external_agent_accuracy = result['result'].sixty_days_data.externalerrors;
        var ninty_days_external_agent_accuracy = result['result'].ninty_days_data.externalerrors;
        var widget_2 = "<div id='widget-75-agent-accuracy' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_4 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_5 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_6 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>"

        var total_agent_accuracy = [thirty_days_external_agent_accuracy, sixty_days_external_agent_accuracy, ninty_days_external_agent_accuracy];

        var cards_2 = [card_html_4, card_html_5, card_html_6];
        for(var k = 0; k<total_agent_accuracy.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_agent_accuracy[k])){
            rows[i]+=rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_agent_accuracy[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards_2[k]+=rows[i];
          cards_2[k]+="</div>";
        }

        card_html_4=cards_2[0]+"</div>";
        card_html_5=cards_2[1]+"</div>";
        card_html_6=cards_2[2]+"</div>";
        widget_2+=card_html_4+card_html_5+card_html_6+"</div>";
        $(".widget-75b highcharts").remove()
        $('.widget-75b').css('overflow','auto');
        var $el = $(widget_2).appendTo(".widget-body.widget-75b");
        $compile($el)($scope);

        $('.widget-75a').removeClass('widget-loader-show');
        $('.widget-75b').removeClass('widget-data-hide');
      }
    });
  };

    self.static_internal_external_unaudited_packet = function(){
    var url = '/api/unaudited_packet/?'+self.static_widget_data;
    return $http({'method':'GET', 'url':url}).success(function(result){
      if(isEmpty(result['result'].thirty_days_data.internalerrors)&&isEmpty(result['result'].sixty_days_data.internalerrors)&&isEmpty(result['result'].ninty_days_data.internalerrors)){
        var table_html = '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold; display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-76b highcharts").remove();
        $('.widget-76b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-76b");
        $compile($el)($scope);
        $('.widget-76a').removeClass('widget-loader-show');
        $('.widget-76b').removeClass('widget-data-hide');
      }else{
        $('.widget-76a').addClass('widget-loader-show');
        $('.widget-76b').addClass('widget-data-hide');
        $("#widget-76-unaudited-packets").remove();
        var thirty_days_internal_unaudited_packet = result['result'].thirty_days_data.internalerrors;
        var sixty_days_internal_unaudited_packet = result['result'].sixty_days_data.internalerrors;
        var ninty_days_internal_unaudited_packet = result['result'].ninty_days_data.internalerrors;
        var widget = "<div id='widget-76-unaudited-packets' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_1 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_2 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_3 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var cards = [card_html_1, card_html_2, card_html_3];
        var total_unaudited_packet = [thirty_days_internal_unaudited_packet, sixty_days_internal_unaudited_packet, ninty_days_internal_unaudited_packet];

        for(var k = 0; k<total_unaudited_packet.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_unaudited_packet[k])){
            rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_unaudited_packet[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards[k]+=rows[i];
          cards[k]+="</div>";
        }

        card_html_1=cards[0]+"</div>";
        card_html_2=cards[1]+"</div>";
        card_html_3=cards[2]+"</div>";
        widget+=card_html_1+card_html_2+card_html_3+"</div>";

        $(".widget-76b highcharts").remove();
        $('.widget-76b').css('overflow','auto');
        var $el = $(widget).appendTo(".widget-body.widget-76b");
        $compile($el)($scope);
        $('.widget-76a').removeClass('widget-loader-show');
        $('.widget-76b').removeClass('widget-data-hide');
      }

     // ===================For External Errors =========================

      if(isEmpty(result['result'].thirty_days_data.externalerrors)&&isEmpty(result['result'].sixty_days_data.externalerrors)&&isEmpty(result['result'].ninty_days_data.externalerrors)){
        var table_html= '<div style="margin-top:100px;font-size:11px; color:#5b5b5b; font-weight:bold;display:flex; justify-content:center;"><span>No data to display</span></div>';
        $(".widget-77b highcharts").remove();
        $('.widget-77b').css('overflow','auto');
        var $el = $(table_html).appendTo(".widget-body.widget-77b");
        $compile($el)($scope);
        $('.widget-77a').removeClass('widget-loader-show');
        $('.widget-77b').removeClass('widget-data-hide');

      }else{
        $('.widget-77a').addClass('widget-loader-show');
        $('.widget-77b').addClass('widget-data-hide');
        $("#widget-77-unaudited-packets").remove();
        var thirty_days_external_unaudited_packet = result['result'].thirty_days_data.externalerrors;
        var sixty_days_external_unaudited_packet = result['result'].sixty_days_data.externalerrors;
        var ninty_days_external_unaudited_packet = result['result'].ninty_days_data.externalerrors;
        var widget_2 = "<div id='widget-77-unaudited-packets' style='margin-top:20px; display:flex; justify-content:center;'>";
        var card_html_4 = "<div class='card'><div class='card-header'><span class='card-header-text'>30 Days</span></div><div class='card-body'>";

        var card_html_5 = "<div class='card'><div class='card-header'><span class='card-header-text'>60 Days</span></div><div class='card-body'>";

        var card_html_6 = "<div  class='card'><div class='card-header'><span class='card-header-text'>90 Days</span></div><div class='card-body'>";

        var total_unaudited_packet = [thirty_days_external_unaudited_packet, sixty_days_external_unaudited_packet, ninty_days_external_unaudited_packet];

        var cards_2 = [card_html_4, card_html_5, card_html_6];
        for(var k = 0; k<total_unaudited_packet.length; k++){
          var rows = ['', '', '', '', ''];
          for(var [i, key] of enumerate(total_unaudited_packet[k])){
            rows[i]+=rows[i]+="<div class='small-card'><h4 class='small-card-body'>"+key+"</h4><p class='badge'>"+total_unaudited_packet[k][key]+"</p></div>";
          }

          for(var i =0; i<rows.length; i++)
            cards_2[k]+=rows[i];
          cards_2[k]+="</div>";
        }

        card_html_4=cards_2[0]+"</div>";
        card_html_5=cards_2[1]+"</div>";
        card_html_6=cards_2[2]+"</div>";
        widget_2+=card_html_4+card_html_5+card_html_6+"</div>";
        $(".widget-77b highcharts").remove()
        $('.widget-77b').css('overflow','auto');
        var $el = $(widget_2).appendTo(".widget-body.widget-77b");
        $compile($el)($scope);

        $('.widget-77a').removeClass('widget-loader-show');
        $('.widget-77b').removeClass('widget-data-hide');
      }
    });
  };

                    self.No_of_agents_AHT = function(final_work,type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        self.type = type;
                        
                        var aht_var = '/api/no_of_agents_AHT/'+self.aht_data_to_show + type + '&chart_name=63';

                        return $http({method:"GET", url: aht_var}).success(function(result){

                            var date_list = result.result.date;
                            var agent_count = result.result.aht_Num_data;
                            var is_annotation = result.result.is_annotation;
                            
                            
                            if (self.list_object.no_of_agents_AHT_daywise != undefined) {

                                if(self.list_object.no_of_agents_AHT_daywise.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.no_of_agents_AHT_daywise.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'ight';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }

                            angular.extend(self.chartOptions68, {
                                   xAxis: {
                                        categories: date_list,
                                    },
                                    legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    },

                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: false,
                                            valueDecimals: 2,

                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: { 
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '63<##>'+self.type+'<##>'+sub_proj+'<##>'+workpack+'<##>'+sub_pack;
                                                    this['project_live'] = self.project_live;
                                                    this['center_live'] = self.center_live;
                                                    return new Annotation(str, $(self.chartOptions68.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            }
                                        }
                                    },
                                    series: agent_count,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){  
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=63&proj_name='+self.project_live+'&cen_name='+
                      self.center_live}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("63", $(self.chartOptions68.chart.renderTo),
                                        chart, point, annotation);

                                   console.log(a);
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    self.annot_perm();
                                    }
                                  }
                                });
                            $('.widget-63a').removeClass('widget-loader-show');
                            $('.widget-63b').removeClass('widget-data-hide');
                        })
                    }


                    
                    
                    self.Percentage_less_aht = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var aht_val = '/api/percentage_60_aht/'+self.data_to_show + type + final_work + '&chart_name=64';

                        return $http({method:"GET", url: aht_val}).success(function(result){

                            var date_list = result.result.date;
                            var agent_count = result.result.aht_percentage;
                            var is_annotation = result.result.is_annotation;
 
                            angular.extend(self.chartOptions69.yAxis,{
                                min:result.result.min_max.min_value,
                                max:result.result.min_max.max_value
                            });
                          if (self.list_object.percentage_people_67_and_99_achieved != undefined) {

                                if(self.list_object.percentage_people_67_and_99_achieved.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.percentage_people_67_and_99_achieved.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }


                            angular.extend(self.chartOptions69, {
                                   xAxis: {
                                        categories: date_list,
                                    },
                                   legend: {
                                        align: align,
                                        verticalAlign:ver_align,
                                        layout: layout
                                    }, 
                              
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: false,
                                            format: '{y} %',
                                            valueDecimals: 2,
                                            formatter: function () {
                                                return Highcharts.numberFormat(this.y, null, null, ",");
                                            },
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: { 
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '64<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project_live'] = self.project_live;
                                                    this['center_live'] = self.center_live;
                                                    return new Annotation(str, $(self.chartOptions69.chart.renderTo),this.series.chart, this);
                                                   }
                                                  }
                                                }
                                            }
                                        }
                                    },
                                    series: agent_count,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;

                                    for(var i in chart_data){  
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=69&proj_name='+self.project_live+'&cen_name='+
                      self.center_live}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("64", $(self.chartOptions69.chart.renderTo),
                                        chart, point, annotation);

                                   console.log(a);
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    self.annot_perm();
                                    }
                                  }
                                });
                            $('.widget-64a').removeClass('widget-loader-show');
                            $('.widget-64b').removeClass('widget-data-hide');
                        })
                    }

                    self.pre_scan = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }
                        self.type = type;

                        var pre_scan = '/api/pre_scan_exce/'+self.data_to_show + type + final_work;

                        return $http({method:"GET", url: pre_scan + '&chart_name=35' }).success(function(result){

                            var date_list  = result.result.date;
                            var pre_scan_details = result.result.pre_scan_exception_data;
                            var is_annotation = result.result.is_annotation;
                
                            if (self.list_object.pre_scan_exception_chart != undefined) {
                        
                                if (self.list_object.pre_scan_exception_chart.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }
                            if (self.list_object.pre_scan_exception_chart != undefined) {

                                if(self.list_object.pre_scan_exception_chart.legends_align == 'bottom') {
                                
                                    var align = 'center';
                                    var ver_align = 'bottom';
                                    var layout = 'horizontal';
                            
                                }
                            
                                else if(self.list_object.pre_scan_exception_chart.legends_align == 'left'){
                            
                                    var align ='left';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            
                                else {
                                    var align = 'right';
                                    var ver_align = 'top';
                                    var layout = 'vertical';
                                }
                            }
                            
                            else {
                                var align = 'center';
                                var ver_align = 'bottom';
                                var layout = 'horizontal';
                            }
                            angular.extend(self.chartOptions40, {

                                xAxis: {
                                    categories: date_list,
                                title: {
                                    text: '',
                                 }
                               },
                               legend: {
                                align: align,
                                verticalAlign:ver_align,
                                layout: layout
                            },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) { 
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '35<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                return new Annotation(str, $(self.chartOptions40.chart.renderTo),this.series.chart, this);
                                                }
                                              }
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                var name = this.name;
                                                var visible = this.visibility;
                                                var chart_name = self._pre_data;
                                                self.data_value.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });                                                
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-35a').children(".widget-35b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                }
                                            },
                                            show: function() {
                                                var name = this.name;
                                                var visible = this.visibility;
                                                var chart_name = self._pre_data;
                                                self.data_value.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });                                                
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-35a').children(".widget-35b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                }
                                            }
                                        }
                                    }
                                },
                               series: pre_scan_details,
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;
                                self.data_value = [];
                                self._pre_data = [];
                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                          self.type+'&chart_name=35&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("35", $(self.chartOptions40.chart.renderTo),
                                    chart, point, annotation);
                               window.data_value = a;
                               self.data_value.push(a);
                               self._pre_data.push(series.name);
                               self.annot_perm();
                               }
                          })
                                    });
                                    }(series));
                                }
                                }
                              }  
                            });
                            $('.widget-35a').removeClass('widget-loader-show');
                            $('.widget-35b').removeClass('widget-data-hide');
                        }) 
                    }
        
                   self.nw_exce = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }
                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var nw_exce = '/api/nw_exce/'+self.data_to_show + type + final_work + '&chart_name=37';

                        return $http({method:"GET", url: nw_exce}).success(function(result){
                                                                    
                            var date_list  = result.result.date;
                            var nw_details = result.result.nw_exception_details;
                            var is_annotation = result.result.is_annotation;

                            if (self.list_object.nw_exception_chart != undefined) {

                                if (self.list_object.nw_exception_chart.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }   
                            }
                            else {
                                var value = false;
                            }
                            angular.extend(self.chartOptions42, {

                                xAxis: {
                                    categories: date_list,
                                title: {
                                    text: '',
                                 }
                               },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                            var str = '37<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                return new Annotation(str, $(self.chartOptions42.chart.renderTo),this.series.chart, this);
                                                }
                                              }  
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                var name = this.name;
                                                var visibility = this.visible;
                                                var chart_name = self._nw_data;
                                                self.Obj.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });                                                
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-37a').children(".widget-37b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                }
                                            },
                                            show: function() {
                                                var name = this.name;
                                                var visibility = this.visible;
                                                var chart_name = self._nw_data;
                                                self.Obj.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });                                                
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-37a').children(".widget-37b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                }
                                            }
                                        }
                                    }
                                },

                               series: nw_details,
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;
                                self.Obj = [];
                                self._nw_data = [];
                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=37&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("37", $(self.chartOptions42.chart.renderTo),
                                    chart, point, annotation);
                               window.Obj = a;
                               self.Obj.push(a);
                               self._nw_data.push(series.name);
                               self.annot_perm();
                               }
                           })
                                    });
                                    }(series));
                                }
                                }
                              }  
                            });
                            $('.widget-37a').removeClass('widget-loader-show');
                            $('.widget-37b').removeClass('widget-data-hide');
                        })
                    }

                    self.overall_exce = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }   

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var overall_exce = '/api/overall_exce/'+self.data_to_show + type + final_work + '&chart_name=36';

                        return $http({method:"GET", url: overall_exce}).success(function(result){
                                                                    
                            var date_list  = result.result.date;
                            var overall_details = result.result.overall_exception_details;
                            var is_annotation = result.result.is_annotation;

                            if (self.list_object.overall_exception_chart != undefined) {
                                
                                if (self.list_object.overall_exception_chart.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                            angular.extend(self.chartOptions41, {

                                xAxis: {
                                    categories: date_list,
                                title: {
                                    text: '',
                                 }
                               },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                            var str = '36<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                return new Annotation(str, $(self.chartOptions41.chart.renderTo),this.series.chart, this);
                                                }
                                              }
                                            }
                                        },
                                        events: {
                                            hide: function() {
                                                var name = this.name;
                                                var visibility = this.visible;
                                                var chart_name = self._overall;
                                                self.Obj_val.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });                                                
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-36a').children(".widget-36b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                }
                                            },
                                            show: function() {
                                                var name = this.name;
                                                var visibility = this.visible;
                                                var chart_name = self._overall;
                                                self.Obj_val.forEach(function(value_data){
                                                    value_data.redraw(name, visibility);
                                                });                                                
                                                if (chart_name.indexOf(name) >= 0) {
                                                    $(document).find('.widget-36a').children(".widget-36b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                }
                                            }
                                        }
                                    }
                                },

                               series: overall_details,
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;
                                self.Obj_val = [];
                                self._overall = [];
                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=36&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("36", $(self.chartOptions41.chart.renderTo),
                                    chart, point, annotation);
                               window.Obj_val = a;
                               self.Obj_val.push(a);
                               self._overall.push(series.name);
                               self.annot_perm();
                               }
                           })
                                    });
                                    }(series));
                                }
                                }
                              }
                            });
                            $('.widget-36a').removeClass('widget-loader-show');
                            $('.widget-36b').removeClass('widget-data-hide');
                        })
                    }
                
                    self.upload_acc = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var upload_acc = '/api/upload_acc/'+self.data_to_show + type + final_work + '&chart_name=34';

                        return $http({method:"GET", url: upload_acc}).success(function(result){

                            var date_list  = result.result.upload_target_data.date;
                            var upload_target_data = result.result.upload_target_data.data;
                            var is_annotation = result.result.is_annotation;

                            if (self.list_object.target_upload_graph != undefined) {

                                if (self.list_object.target_upload_graph.display_value === true) {
                                    
                                    var value = true;
                                }
                                
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                            angular.extend(self.chartOptions39, {

                                xAxis: {
                                    categories: date_list,
                                title: {
                                    text: '',
                                 }
                               },
                                plotOptions: {
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                             else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '34<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                return new Annotation(str, $(self.chartOptions39.chart.renderTo),this.series.chart, this);
                                                }
                                              }  
                                            }
                                        }
                                    }
                                },

                               series: upload_target_data,
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;

                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=34&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){ 
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("34", $(self.chartOptions39.chart.renderTo),
                                    chart, point, annotation);
                               self.annot_perm();
                               }
                           })
                                    });
                                    }(series));
                                }
                                }
                              }
                            });
                            $('.widget-34a').removeClass('widget-loader-show');
                            $('.widget-34b').removeClass('widget-data-hide');
                        })
                    }
                
            self.error_field_graph = function(err_field_graph){

                       if (self.err_field.length == 1) {

                       return $http({method:"GET", url: err_field_graph + '&chart_name=38&chart_name=39'}).success(function(result){
                            var is_annotation = result.result.is_annotation;
                           angular.extend(self.chartOptions43.yAxis,{
                                min:result.result.internal_min_max.min_value,
                                max:result.result.internal_min_max.max_value
                            });

                            if (self.list_object.internal_field_accuracy_graph != undefined) {

                                if (self.list_object.internal_field_accuracy_graph.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }                                       
                            }
                            else {
                                var value = false;
                            }

                           angular.extend(self.chartOptions43,{
                                plotOptions: { 
                                    series: {
                                      dataLabels: {
                                        enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '38<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions43.chart.renderTo),this.series.chart, this);
                                                }
                                            }
                                          }
                                        }
                                    }
                                },
                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.internal_field_accuracy_graph
                               }],
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;

                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=38&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){  
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("38", $(self.chartOptions43.chart.renderTo),
                                    chart, point, annotation);
                               self.annot_perm();
                               }
                           })   
                                    });
                                    }(series));
                                }
                                }
                              }  
                           });
                            $('.widget-38a').removeClass('widget-loader-show');
                            $('.widget-38b').removeClass('widget-data-hide');

                           angular.extend(self.chartOptions44.yAxis,{
                                min:result.result.external_min_max.min_value,
                                max:result.result.external_min_max.max_value
                            });

                            if (self.list_object.external_field_accuracy_graph != undefined) {

                                if (self.list_object.external_field_accuracy_graph.display_value === true) {

                                    var value = true;
                                }
                                
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                           angular.extend(self.chartOptions44,{
                                plotOptions: { 
                                    series: {
                                      dataLabels: {
                                         enabled: value,
                                      },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '39<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                               this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions44.chart.renderTo),this.series.chart, this);
                                                }
                                            }
                                           } 
                                        }
                                    }
                                },
                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.external_field_accuracy_graph
                               }],
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;

                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=39&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){  
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("39", $(self.chartOptions44.chart.renderTo),
                                    chart, point, annotation);
                               window.annotObj = a;
                               self.annot_perm();
                               }
                           })   
                                    });
                                    }(series));
                                }
                                }
                              }
                           });
                           $('.widget-39a').removeClass('widget-loader-show');
                           $('.widget-39b').removeClass('widget-data-hide');
                       })
                 }
            }

            self.error_bar_graph = function(error_bar_graph){
                            
                           if (self.bar_acc.length == 1) {
                           return $http({method:"GET", url: error_bar_graph + '&chart_name=2&chart_name=3'}).success(function(result){
                            var is_annotation = result.result.is_annotation;
                            if (self.list_object.internal_error_accuracy != undefined) {

                                if (self.list_object.internal_error_accuracy.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                           angular.extend(self.chartOptions4.yAxis,{
                                min:result.result.internal_min_max.min_value,
                                max:result.result.internal_min_max.max_value
                            });
                           angular.extend(self.chartOptions4,{
                                plotOptions: {
                                    series: {
                                        dataLabels: {
                                            enabled: value,
                                            format: '{y} %',
                                            valueDecimals: 2
                                        },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '2<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions4.chart.renderTo),this.series.chart, this);
                                                }
                                              }
                                            }
                                        }
                                    }
                                },
                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.internal_accuracy_graph
                               }],
                                onComplete: function(chart){
                                if (is_annotation){
                                var series = null;
                                var chart_data = chart.series;

                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=2&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type=bar'}).success(function(annotations){  
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("2", $(self.chartOptions4.chart.renderTo),
                                    chart, point, annotation);
                               window.annotObj = a;
                               self.annot_perm();
                               }
                           })
                                    });
                                    }(series));
                                }
                                }
                              }   
                           });
                           $('.widget-2a').removeClass('widget-loader-show');
                           $('.widget-2b').removeClass('widget-data-hide');

                           angular.extend(self.chartOptions6.yAxis,{
                                min:result.result.external_min_max.min_value,
                                max:result.result.external_min_max.max_value
                            });

                            if (self.list_object.external_error_accuracy != undefined) {

                                if (self.list_object.external_error_accuracy.display_value === true) {

                                    var value = true;
                                }
                                else {
                                    var value = false;
                                }
                            }
                            else {
                                var value = false;
                            }

                           angular.extend(self.chartOptions6,{
                                plotOptions: {
                                    series: {
                                        dataLabels: {
                                            enabled: value,
                                            format: '{y} %',
                                            valueDecimals: 2
                                        },
                                      allowPointSelect: true,
                                      cursor: 'pointer',
                                        point: {
                                          events:{
                                            contextmenu: function() {
                                             if (self.role_for_perm == 'customer') {

                                                console.log('he is customer');
                                             }
                                             else {

                                              if (self.data_to_show.split('&').length == 6) {
                                                var sub_proj = '';
                                                var work_pack = '';
                                                var sub_pack = '';
                                              }
                                              else {
                                                var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                              }
                                                var str = '3<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                this['project'] = self.project_live;
                                                this['center'] = self.center_live;
                                                this['from'] = self.start_date;
                                                this['to'] = self.end_date;
                                                this['chart_type'] = 'bar';
                                                return new Annotation(str, $(self.chartOptions6.chart.renderTo),this.series.chart, this);
                                                }
                                              }
                                            }
                                        }
                                    }
                                },

                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.external_accuracy_graph
                               }],
                                onComplete: function(chart){
                                if (is_annotation) {
                                var series = null;
                                var chart_data = chart.series;

                                for(var i in chart_data){
                                    series = chart_data[i];
                                    (function(series){
                                      $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+
                      self.type+'&chart_name=3&project='+self.project_live+'&center='+
                      self.center_live+'&from='+self.start_date+'&to='+self.end_date+'&chart_type='+'bar'}).success(function(annotations){  
                           annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                           $.each(annotations, function(j, annotation){

                             var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                             point = point[0];

                             if(annotation.epoch){
                               var a = new Annotation("3", $(self.chartOptions6.chart.renderTo),
                                    chart, point, annotation);
                               window.annotObj = a;
                               self.annot_perm();
                               }
                           })

                                    });
                                    }(series));
                                }
                                }
                              }  
                           });
                           $('.widget-3a').removeClass('widget-loader-show');
                           $('.widget-3b').removeClass('widget-data-hide');
                       })
                 }
            }

                    self.from_to = function(final_work, type, name) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        if (name == undefined) {
                            name = ''
                        }

                        self.type = type;

                        if ((self.acc_timeline.length == 1) || (type == 'week') || (type == 'month') || (self.button_clicked == "day_yes")) {

                        var from_to = '/api/from_to/'+self.data_to_show + type + final_work + '&chart_name=7&chart_name=8';

                        return $http({method:"GET", url: from_to}).success(function(result){

                            var internal_date_list = result.result.internal_date;
                            var external_date_list = result.result.external_date;
                            var external_error_timeline = result.result.external_accuracy_timeline;
                            var internal_error_timeline = result.result.internal_accuracy_timeline;
                            var is_annotation = result.result.is_annotation;

                            if ((name == "self.chartOptions9_2") || (name == "")) {
                            
                                if (self.list_object.external_accuracy_timeline != undefined) {

                                    if (self.list_object.external_accuracy_timeline.display_vaue === true) {

                                        var value = true;
                                    }
                                    else {
                                        var value = false;
                                    }  
                                }
                                else {
                                    var value = false;
                                }

                                angular.extend(self.chartOptions9_2.yAxis,{
                                    min:result.result.min_external_time_line,
                                    max:result.result.max_external_time_line
                                });

                                angular.extend(self.chartOptions9_2, {
                                    xAxis: {
                                        categories: external_date_list,
                                    },
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                            format: '{y} %',
                                            valueDecimals: 2
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '7<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions9_2.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }  
                                                }
                                            },
                                            events: {
                                                hide: function() {
                                                    var name =  this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._accuracy_lines;
                                                    self.Obj_data.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });                                                    
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-7a').children(".widget-7b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name =  this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._accuracy_lines;
                                                    self.Obj_data.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });                                                    
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-7a').children(".widget-7b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    series: external_error_timeline,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self.Obj_data = [];
                                    self._accuracy_lines = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+self.type+'&chart_name=7&project='+self.project_live+'&center='+
                                           self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});
                                 point = point[0];
                                 if(annotation.epoch){
                                   var a = new Annotation("7", $(self.chartOptions9_2.chart.renderTo),
                                        chart, point, annotation);
                                   window.Obj_data = a;
                                   self.Obj_data.push(a);
                                   self._accuracy_lines.push(series.name);
                                   self.annot_perm();
                                   }
                               })
                                        });
                                        }(series));
                                    }
                                    }
                                  }
                                });
                            }
                                $('.widget-7a').removeClass('widget-loader-show');
                                $('.widget-7b').removeClass('widget-data-hide');

                            if ((name == "self.chartOptions9") || (name == "")) {

                                if (self.list_object.internal_accuracy_timeline != undefined) {

                                    if (self.list_object.internal_accuracy_timeline.display_value === true) {

                                        var value = true;
                                    }
                                    else {
                                        var value = false;
                                    }
                                }
                                else {
                                    var value = false;
                                }

                                angular.extend(self.chartOptions9.yAxis,{
                                    min:result.result.min_internal_time_line,
                                    max:result.result.max_internal_time_line
                                });

                                angular.extend(self.chartOptions9, {
                                    xAxis: {
                                        categories: internal_date_list,
                                    },
                                    plotOptions: {
                                        series: {
                                          dataLabels: {
                                            enabled: value,
                                            format: '{y} %',
                                            valueDecimals: 2
                                          },
                                          allowPointSelect: true,
                                          cursor: 'pointer',
                                            point: {
                                              events:{ 
                                                contextmenu: function() {
                                                 if (self.role_for_perm == 'customer') {

                                                    console.log('he is customer');
                                                 }
                                                 else {

                                                  if (self.data_to_show.split('&').length == 6) {
                                                    var sub_proj = '';
                                                    var work_pack = '';
                                                    var sub_pack = '';
                                                  }
                                                  else {
                                                    var sub_proj = self.data_to_show.split('&')[5].split('=')[1];
                                                    var work_pack = self.data_to_show.split('&')[6].split('=')[1];
                                                    var sub_pack = self.data_to_show.split('&')[7].split('=')[1]
                                                  }
                                                    var str = '8<##>'+self.type+'<##>'+sub_proj+'<##>'+work_pack+'<##>'+sub_pack;
                                                    this['project'] = self.project_live;
                                                    this['center'] = self.center_live;
                                                    this['from'] = self.start_date;
                                                    this['to'] = self.end_date;
                                                    return new Annotation(str, $(self.chartOptions9.chart.renderTo),this.series.chart, this);
                                                    }
                                                  }
                                                }
                                            },
                                           events: {
                                                hide: function() {
                                                    var name  = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._accu_intrnl;
                                                    self.annotObj.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });                                                    
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-8a').children(".widget-8b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 0);
                                                    }
                                                },
                                                show: function() {
                                                    var name  = this.name;
                                                    var visibility = this.visible;
                                                    var chart_name = self._accu_intrnl;
                                                    self.annotObj.forEach(function(value_data){
                                                        value_data.redraw(name, visibility);
                                                    });                                                    
                                                    if (chart_name.indexOf(name) >= 0) {
                                                        $(document).find('.widget-8a').children(".widget-8b").find('.annotation-marker[series-name="'+name+'"]').css("opacity", 1);
                                                    }
                                                }
                                            }
                                        }
                                    },

                                    series: internal_error_timeline,
                                    onComplete: function(chart){
                                    if (is_annotation) {
                                    var series = null;
                                    var chart_data = chart.series;
                                    self.annotObj = [];
                                    self._accu_intrnl = [];
                                    for(var i in chart_data){
                                        series = chart_data[i];
                                        self.annotObj = [];
                                        (function(series){
                                          $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type='+self.type+'&chart_name=8&project='+self.project_live+'&center='+
                                           self.center_live+'&from='+self.start_date+'&to='+self.end_date}).success(function(annotations){  
                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });
                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("8", $(self.chartOptions9.chart.renderTo),
                                        chart, point, annotation);
                                   window.annotObj = a;
                                   self.annotObj.push(a);
                                   self._accu_intrnl.push(series.name);
                                   self.annot_perm();
                                   }
                               })

                                        });
                                        }(series));
                                    }
                                    }
                                  }  
                                });
                                $('.widget-8a').removeClass('widget-loader-show');
                                $('.widget-8b').removeClass('widget-data-hide');
                            }

                         })
                        }
                       }
                self.hideLoading();

        var static_ajax = static_data + self.static_widget_data;
        self.static_data_call = function(static_ajax){
                
            if (self.list_object.Static_Monthly_Production_Trend != undefined) {

                if(self.list_object.Static_Monthly_Production_Trend.legends_align == 'bottom') {
                
                    var align1 = "center";                    
                    var ver_align1 = "bottom";
                    var layout1 = "horizontal";
            
                }
            
                else if(self.list_object.Static_Monthly_Production_Trend.legends_align == 'left'){
            
                    var align1 = "left";
                    var ver_align1 = "top";
                    var layout1 = "vertical";
                }
            
                else {
                    var align1 = "right";
                    var ver_align1 = "top";
                    var layout1 = "vertical";
                }
            }
            
            else {
                var align1 = "center";
                var ver_align1 = "bottom";
                var layout1 = "horizontal";
            }  
            
            if (self.list_object.Static_Weekly_Production_Trend != undefined) {

                if(self.list_object.Static_Weekly_Production_Trend.legends_align == 'bottom') {
                
                    var align2 = "center";
                    var ver_align2 = "bottom";
                    var layout2 = "horizontal";
            
                }
            
                else if(self.list_object.Static_Weekly_Production_Trend.legends_align == 'left'){
            
                    var align2 = "left";
                    var ver_align2 = "top";
                    var layout2 = "vertical";
                }
            
                else {
                    var align2 = "right";
                    var ver_align2 = "top";
                    var layout2 = "vertical";
                }
            }
            
            else {
                var align2 = "center";
                var ver_align2 = "bottom";
                var layout2 = "horizontal";
            }
            
            if (self.list_object.Static_Daily_Production_Trend != undefined) {

                if(self.list_object.Static_Daily_Production_Trend.legends_align == 'bottom') {
                
                    var align3 = "center";
                    var ver_align3 = "bottom";
                    var layout3 = "horizontal";
            
                }
            
                else if(self.list_object.Static_Daily_Production_Trend.legends_align == 'left'){
            
                    var align3 = "left";
                    var ver_align3 = "top";
                    var layout3 = "vertical";
                }
            
                else {
                    var align3 = "right";
                    var ver_align3 = "top";
                    var layout3 = "vertical";
                }
            }
            
            else {
                var align3 = "center";
                var ver_align3 = "bottom";
                var layout3 = "horizontal";
            }
            
            if (self.list_object.Static_Daily_Production_Bar != undefined) {

                if(self.list_object.Static_Daily_Production_Bar.legends_align == 'bottom') {
                
                    var align4 = "center";
                    var ver_align4 = "bottom";
                    var layout4 = "horizontal";
            
           	} 
                else if(self.list_object.Static_Daily_Production_Bar.legends_align == 'left'){
            
                    var align4 = "left";
                    var ver_align4 = "top";
                    var layout4 = "vertical";
                }
            
                else {
                    var align4 = "right";
                    var ver_align4 = "top";
                    var layout4 = "vertical";
                }
            }
            
            else {
                var align4 = "center";
                var ver_align4 = "bottom";
                var layout4 = "horizontal";
            }

            if (self.list_object.Static_Weekly_Production_Bar != undefined) {

                if(self.list_object.Static_Weekly_Production_Bar.legends_align == 'bottom') {
                
                    var align5 = "center";
                    var ver_align5 = "bottom";
                    var layout5 = "horizontal";
            
                }
            
                else if(self.list_object.Static_Weekly_Production_Bar.legends_align == 'left'){
            
                    var align5 = "left";
                    var ver_align5 = "top";
                    var layout5 = "vertical";
                }
            
                else {
                    var align5 = "right";
                    var ver_align5 = "top";
                    var layout5 = "vertical";
                }
            }
            
            else {
                var align5 = "center";
                var ver_align5 = "bottom";
                var layout5 = "horizontal";
            }

            if (self.list_object.Static_Monthly_Production_Bar != undefined) {

                if(self.list_object.Static_Monthly_Production_Bar.legends_align == 'bottom') {
                
                    var align6 = "center";
                    var ver_align6 = "bottom";
                    var layout6 = "horizontal";
            
                }
            
                else if(self.list_object.Static_Monthly_Production_Bar.legends_align == 'left'){
            
                    var align6 = "left";
                    var ver_align6 = "top";
                    var layout6 = "vertical";
                }
            
                else {
                    var align6 = "right";
                    var ver_align6 = "top";
                    var layout6 = "vertical";
                }
            }
            
            else {
                var align6 = "center";
                var ver_align6 = "bottom";
                var layout6 = "horizontal";
            }
            if (self.stacti_list.length == 1) {
                
                $http({method:"GET", url:static_ajax}).success(function(result){
                    angular.extend(self.chartOptions32, {
                        xAxis: {
                            categories: result.result.month_productivity_data.date,
                        title: {
                            text: '',
                         },
                         legend: {
                            align: align1,
                            verticalAlign:ver_align1,
                            layout: layout1
                        },
                
                       },

                       series: result.result.month_productivity_data.data
                    });                   
                    $('.widget-27a').removeClass('widget-loader-show');
                    $('.widget-27b').removeClass('widget-data-hide');

                    angular.extend(self.chartOptions33, {
                        xAxis: {
                            categories: result.result.week_productivity_data.date,
                        title: {
                            text: '',
                         },
                         legend: {
                            align: align2,
                            verticalAlign:ver_align2,
                            layout: layout2
                        },
                       },

                       series: result.result.week_productivity_data.data
                    });
                    $('.widget-28a').removeClass('widget-loader-show');
                    $('.widget-28b').removeClass('widget-data-hide');

                    angular.extend(self.chartOptions34, {
                        xAxis: {
                            categories: result.result.date,
                        title: {
                            text: '',
                         },
                         legend: {
                            align: align3,
                            verticalAlign:ver_align3,
                            layout: layout3
                        },
                       },

                       series: result.result.data
                    });
                    $('.widget-29a').removeClass('widget-loader-show');
                    $('.widget-29b').removeClass('widget-data-hide');

                    angular.extend(self.chartOptions35, {
                        xAxis: {
                            categories: result.result.date,
                        title: {
                            text: '',
                         },
                         legend: {
                            align: align4,
                            verticalAlign:ver_align4,
                            layout: layout4
                        },
                       },

                       series: result.result.data
                    });
                    $('.widget-30a').removeClass('widget-loader-show');
                    $('.widget-30b').removeClass('widget-data-hide');

                    angular.extend(self.chartOptions36, {
                        xAxis: {
                            categories: result.result.week_productivity_data.date,
                        title: {
                            text: '',
                         }
                       },
                       legend: {
                        align: align5,
                        verticalAlign:ver_align5,
                        layout: layout5
                    },

                       series: result.result.week_productivity_data.data
                    });
                    $('.widget-31a').removeClass('widget-loader-show');
                    $('.widget-31b').removeClass('widget-data-hide');

                    angular.extend(self.chartOptions37, {
                        xAxis: {
                            categories: result.result.month_productivity_data.date,
                        title: {
                            text: '',
                         },
                        },
                         legend: {
                            align: align6,
                            verticalAlign:ver_align6,
                            layout: layout6
                        },
                       

                       series: result.result.month_productivity_data.data
                    });
                    $('.widget-32a').removeClass('widget-loader-show');
                    $('.widget-32b').removeClass('widget-data-hide');

                });
            }
        }
                                
            self.work_list = [];
            self.stacti_list = [];
            self.prod_list = [];
            self.bar_acc = [];
            self.cate_pie = [];
            self.cate_pareto = [];
            self.agent_pareto = [];
            self.fte_list = [];
            self.err_field = [];
            self.acc_timeline = [];
            self.utili_list = [];
            if (self.is_voice_flag == false) {
                var sort_array = [];
                var final_array = []; 
                for (var key in self.list_object) {
                     sort_array.push({key:key,value:self.list_object[key].widget_priority});
                }
                
                
               sort_array.sort(function(x,y){return x.value - y.value});
                var values_array = [];
                sort_array.forEach( function (eachObj){
                    for (var key in eachObj) {
                        values_array.push(eachObj.key);
                    }
                });
 
                 var names = values_array;
                 var uniqueNames = [];
                 $.each(names, function(i, el){
                     if($.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
                 }); 

                $.each(uniqueNames, function (key, val) {
                    if ((val == 'productivity_chart') || (val == 'productivity_bar_graph')) {
                         self.prod_list.push('production')
                         self.main_prod(undefined, undefined, undefined)
                    } else if (val == 'performance_summary') {
                        self.performance(undefined, undefined,undefined)
                    } else if (val == 'internal_agent_error_data'){
                      self.static_internal_external_agent_errors()
                    } else if (val == 'static_internal_error_category'){
                      self.static_internal_external_error_category()
                    } else if(val == 'internal_packet_wise_error_data'){
                      self.static_internal_external_packet_errors()
                    } else if(val == 'internal_packet_accuracy') {
                      self.static_internal_external_packet_accuracy()
                    } else if(val =='internal_agent_accuracy'){
                      self.static_internal_external_agent_accuracy()
                    } else if(val =='internal_unaudited_packets'){
                      self.static_internal_external_unaudited_packet()
                    } else if (val == 'no_of_agents_AHT_daywise') {
                         self.No_of_agents_AHT(undefined)
                    } else if (val == 'percentage_people_67_and_99_achieved') {
                         self.Percentage_less_aht(undefined, undefined)
                    } else if ((val == 'volume_bar_graph') || (val == 'volume_productivity_graph')) {
                         self.work_list.push('work_track')
                         self.allo_and_comp(undefined, undefined, undefined)
                    } else if ((val == 'fte_utilization') || (val == 'operational_utilization') || (val == 'utilisation_wrt_work_packet')) {
                         self.utili_list.push('utilisation')
                         self.utill_all(undefined, undefined, undefined)
                    } else if ((val == 'sum_total_fte') || (val == 'total_fte')) {
                         self.fte_list.push('fte_graphs')
                         self.fte_graphs(undefined, undefined, undefined)
                    } else if ((val == 'internal_error_accuracy_pie') || (val == 'external_error_accuracy_pie')) {
                         self.cate_pie.push('cate_pie')
                         self.category_error(cate_error)
                    } else if ((val == 'error_category_internal_pareto_analysis') || (val == 'error_category_external_pareto_analysis')) {
                         self.cate_pareto.push('cate_pareto')
                         self.pareto_category_error(pareto_cate_error)
                    } else if ((val == 'agent_wise_pareto_graph_data') || (val == 'agent_wise_external_pareto_analysis')) {
                         self.agent_pareto.push('agent_pareto')
                         self.agent_category_error(agent_cate_error)
                    } else if ((val == 'external_accuracy_timeline') || (val == 'internal_accuracy_timeline')) {
                         self.acc_timeline.push('accuracy_timeline')
                         self.from_to(undefined, undefined, undefined)
                    } else if ((val == 'external_error_accuracy') || (val == 'internal_error_accuracy')) {
                         self.bar_acc.push('bar_accuracy')
                         self.error_bar_graph(error_bar_graph)
                    } else if (val == 'productivity_trends') {
                         self.productivity(undefined, undefined)
                    } else if (val == 'monthly_volume_widget') {
                         self.mont_volume(undefined, undefined)
                    } else if (val == 'production_avg_perday') {
                         self.prod_avg(undefined, undefined)
                    } else if (val == 'target_upload_graph') {
                         self.upload_acc(undefined, undefined)
                    } else if (val == 'pre_scan_exception_chart') {
                         self.pre_scan(undefined, undefined)
                    } else if (val == 'nw_exception_chart') {
                         self.nw_exce(undefined, undefined)
                    } else if (val == 'overall_exception_chart') {
                         self.overall_exce(undefined, undefined)
                    } else if (val == 'aht_team_grpah') {
                         self.aht_data(undefined, undefined)
                    }else if (val == 'tat_graph') {
                         self.tat_data(undefined, undefined)
                    } else if ((val == 'Static_Daily_Production_Trend') || (val == 'Static_Weekly_Production_Trend') || (val == 'Static_Monthly_Production_Trend') || (val == 'Static_Daily_Production_Bar') || (val == 'Static_Weekly_Production_Bar') || (val == 'Static_Monthly_Production_Bar')) {
                         self.stacti_list.push('static')
                         self.static_data_call(static_ajax)
                 } else if ((val == 'internal_field_accuracy_graph') || (val == 'external_field_accuracy_graph')) {
                          self.err_field.push('field_accuracy')
                          self.error_field_graph(err_field_graph)
                    }
                });

            }
        }

             self.packet_data = $http.get(self.pro_landing_url).then(function(result){
                
                self.list_object = result.data.result.lay[0];
                self.layout_list = result.data.result.lay[1].layout;
                self.user_status = result.data.result.user_status;

                self.work_packet = result.data.result.work_packet;
                self.sub_packet = result.data.result.sub_packet;
                self.sub_project = result.data.result.sub_project;

                self.voice_location = result.data.result.location;
                self.voice_skill = result.data.result.skill;
                self.voice_disposition = result.data.result.disposition;

                var pro_cen_nam = $state.params.selpro;                                                                                           
                self.call_back = [];

                self.first = result.data.result.dates.from_date;                                                                                       
                self.last = result.data.result.dates.to_date;

                self.start = self.first;
                self.end = self.last;

                self.call_back.push(self.first);
                self.call_back.push(self.last);

                $('#select').val(self.first + ' to ' + self.last);

                self.final_layout_values_list = {
                    'self.chartOptions':self.chartOptions,
                    'self.chartOptions4':self.chartOptions4,
                    'self.chartOptions6':self.chartOptions6,
                    'self.chartOptions9':self.chartOptions9,
                    'self.chartOptions9_2':self.chartOptions9_2,
                    'self.chartOptions10':self.chartOptions10,
                    'self.chartOptions15':self.chartOptions15,
                    'self.chartOptions15_2':self.chartOptions15_2,
                    'self.chartOptions16':self.chartOptions16,
                    'self.chartOptions16_2':self.chartOptions16_2,
                    'self.chartOptions17':self.chartOptions17,
                    'self.chartOptions18':self.chartOptions18,
                    'self.chartOptions5':self.chartOptions5,
                    'self.chartOptions5_2':self.chartOptions5_2,
                    'self.chartOptions19':self.chartOptions19,
                    'self.chartOptions20':self.chartOptions20,
                    'self.chartOptions21':self.chartOptions21,
                    'self.chartOptions22':self.chartOptions22,
                    'self.chartOptions23':self.chartOptions23,
                    'self.chartOptions24':self.chartOptions24,
                    'self.chartOptions25':self.chartOptions25,
                    'self.chartOptions26':self.chartOptions26,
                    'self.chartOptions27':self.chartOptions27,
                    'self.chartOptions28':self.chartOptions28,
                    'self.chartOptions29':self.chartOptions29,
                    'self.chartOptions30':self.chartOptions30,
                    'self.chartOptions31':self.chartOptions31,
                    'self.chartOptions32':self.chartOptions32,
                    'self.chartOptions33':self.chartOptions33,
                    'self.chartOptions34':self.chartOptions34,
                    'self.chartOptions35':self.chartOptions35,
                    'self.chartOptions36':self.chartOptions36,
                    'self.chartOptions37':self.chartOptions37,
                    'self.chartOptions38':self.chartOptions38,
                    'self.chartOptions39':self.chartOptions39,
                    'self.chartOptions40':self.chartOptions40,
                    'self.chartOptions41':self.chartOptions41,
                    'self.chartOptions42':self.chartOptions42,
                    'self.chartOptions43':self.chartOptions43,
                    'self.chartOptions44':self.chartOptions44,
                    'self.chartOptions45':self.chartOptions45,
                    'self.chartOptions46':self.chartOptions46,
                    "self.chartOptions47":self.chartOptions47,
                    "self.chartOptions48":self.chartOptions48,
                    "self.chartOptions49":self.chartOptions49,
                    "self.chartOptions50":self.chartOptions50,
                    "self.chartOptions51":self.chartOptions51,
                    "self.chartOptions52":self.chartOptions52,
                    "self.chartOptions53":self.chartOptions53,
                    "self.chartOptions54":self.chartOptions54,
                    "self.chartOptions55":self.chartOptions55,
                    "self.chartOptions56":self.chartOptions56,
                    "self.chartOptions57":self.chartOptions57,
                    "self.chartOptions58":self.chartOptions58,
                    "self.chartOptions59":self.chartOptions59,
                    "self.chartOptions60":self.chartOptions60,
                    "self.chartOptions61":self.chartOptions61,
                    "self.chartOptions62":self.chartOptions62,
                    "self.chartOptions63":self.chartOptions63,
                    'self.chartOptions64':self.chartOptions64,
                    'self.chartOptions65':self.chartOptions65,
                    "self.chartOptions68":self.chartOptions68,
                    "self.chartOptions69":self.chartOptions69,
                    "self.chartOptions70":self.chartOptions70
                  };

                self.final_layout_list = [];
                for (var single in self.layout_list){
                    for (var double in self.list_object){
                        if (self.layout_list[single] === double) {
                            self.final_layout_list.push(self.list_object[double])
                        }
                    }
                }

                self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                //self.project = pro_cen_nam.split('-')[1].replace(' ','') + ' - '
                var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                var project_val = project_check.search('&');
                if (project_val != -1) {
                    self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');
                }
                else {
                    self.project = pro_cen_nam.split('-')[1].replace(' ','');
                }
                self.call_back.push(self.location);
                self.call_back.push(self.project);
             
                return self.call_back;

           }).then(function(callback){
                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' +
                                                                self.drop_work_pack;
                    self.voiceTypeFilter = function(key, make_ajax) {
                        if (key != '') {
                            self.voiceProjectType = key; 
                        }
                        var myElement = document.querySelector("#cal_data");
                        myElement.style.marginTop = "25px";
                        $('#select').val(self.first + ' to ' + self.last);
                        var dateEntered = document.getElementById('select').value;
                        dateEntered = dateEntered.replace(' to ','to');
                        var from = dateEntered.split('to')[0].replace(' ','');
                        var to = dateEntered.split('to')[1].replace(' ','');
                        //var from = self.start;
                        //var to = self.end;
                        callback.push.apply(callback, [from, to, self.center_live, self.project_live]);
                        if(key == 'inbound') {
                            $('.inbound').addClass('active btn-success');
                            $('.inbound').siblings().removeClass('active btn-success');
                        } else if (key == 'outbound') {
                            $('.outbound').addClass('active btn-success');
                            $('.outbound').siblings().removeClass('active btn-success');
                        }
                        if(make_ajax) {
                            //var packet_url = '/api/get_packet_details/?&project='+callback[3]+'&center='+callback[2]+'&from='+self.start+'&to='+self.end+'&voice_project_type='+key;
                            var packet_url = '/api/get_packet_details/?&project='+callback[3]+'&center='+callback[2]+'&from='+callback[0]+'&to='+callback[1]+'&voice_project_type='+key;
                            $http.get(packet_url).then(function(result) {
                                self.chartProcess(result);
                                self.checkScroll();
                            }) 
                        }
                    }

                        self.chartProcess = function(result) {
                            $('#dropdown_title').html($(".brand_style").text().replace(" - DASHBOARD",''));
                            self.fin_sub_project = result.data.result.fin.sub_project;
                            self.fin_sub_packet = result.data.result.fin.sub_packet;
                            self.fin_work_packet = result.data.result.fin.work_packet;
                            self.is_voice_flag = result.data.result.is_voice;
                            self.main_day_type = result.data.result.type;
                            self.day_type = result.data.result.type;
                            self.active_filters(self.day_type, '');
                            self.apply_class();
                            if (self.is_voice_flag) {
                                $('#emp_widget').hide();
                                $('#volume_table').hide();
                                self.voiceProjectList = result.data.result.voice_project_types;
                                self.voiceProjectList = ['inbound', 'outbound'];
                                angular.element(document.querySelector('#voice_filter_div')).removeClass('hide');
                                self.voice_filters.Location = result.data.result['location'];
                                self.voice_filters.Skill = result.data.result['skill'];
                                self.voice_filters.Disposition = result.data.result['disposition'];
                                self.LocationFilter = document.getElementById("Location");
                                self.SkillFilter = document.getElementById("Skill");
                                self.DispositionFilter = document.getElementById("Disposition");
                                $(self.LocationFilter.options).remove();
                                $(self.SkillFilter.options).remove();
                                $(self.DispositionFilter.options).remove();
                                if (self.voice_filters.Location.length) {
                                    $(self.LocationFilter).parent().show();
                                    angular.forEach(self.voice_filters.Location, function(location_value) {
                                        self.LocationFilter.options[self.LocationFilter.options.length] = new Option(location_value, location_value);
                                    });
                                } else {
                                    $(self.LocationFilter).parent().hide();
                                }
                                if((self.voice_filters.Skill.length)) {
                                    $(self.SkillFilter).parent().show();
                                    angular.forEach(self.voice_filters.Skill, function(skill_value) {
                                        self.SkillFilter.options[self.SkillFilter.options.length] = new Option(skill_value, skill_value);
                                    });
                                } else {
                                    $(self.SkillFilter).parent().hide();
                                }
                                if ((self.voice_filters.Disposition.length)) {
                                    $(self.DispositionFilter).parent().show();
                                    angular.forEach(self.voice_filters.Disposition, function(disposition_value) {
                                        self.DispositionFilter.options[self.DispositionFilter.options.length] = new Option(disposition_value, disposition_value);
                                    });
                                } else {
                                    $(self.DispositionFilter).parent().hide();
                                }
                                if(!(self.fin_sub_project || self.fin_sub_packet || self.fin_work_packet )) {
                                    self.packet_hierarchy_list = [];
                                }
                                var type = '';
                                //self.voice_filter = '?&project='+callback[3]+'&center='+callback[2]+'&from='+ self.start+'&to='+ self.end + '&type=';
                                self.voice_filter = '?&project='+callback[3]+'&center='+callback[2]+'&from='+ callback[0]+'&to='+ callback[1] + '&type=';
                                if ((self.voice_location != '') && (self.voice_skill != '') && (self.voice_disposition != '')) {
                                    self.locationValue = self.voice_location;
                                    self.skillValue = self.voice_skill;
                                    self.dispositionValue = self.voice_disposition;
                                    
                                } else {
                                    self.locationValue = 'All';
                                    self.skillValue = 'All';
                                    self.dispositionValue = 'All';
                                }
                                self.voiceFilterType = 'location';
                                if(self.is_voice_flag) {
                                    self.ajaxVoiceFilter = function(type, key) {
                                        var voice_filter_ajax = '/api/'+ type + self.voice_filter + self.day_type + '&location=' + self.locationValue + '&skill=' + self.skillValue + '&disposition=' + self.dispositionValue + '&project_type=' + self.voiceProjectType;
                                        var day_type = self.day_type;
                                        if (self.day_type == '') {
                                            var voice_filter_ajax = '/api/'+ type + self.voice_filter + self.main_day_type + '&location=' + self.locationValue + '&skill=' + self.skillValue + '&disposition=' + self.dispositionValue + '&project_type=' + self.voiceProjectType;
                                            var day_type = self.main_day_type;
                                        }
                                        //For Single Widget Type Change
                                        if (key != '') {
                                            var voice_filter_ajax = '/api/'+ type + self.voice_filter + key + '&location=' + self.locationValue + '&skill=' + self.skillValue + '&disposition=' + self.dispositionValue + '&project_type=' + self.voiceProjectType;
                                            var day_type = key;
                                        }
                                        var widgetA, widgetB, type_check;
                                        if(type == self.filter_list[0]) {
                                            widgetA = '.widget-42a';
                                            widgetB = '.widget-42b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[1]) {
                                            widgetA = '.widget-43a';
                                            widgetB = '.widget-43b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[2]) {
                                            widgetA = '.widget-44a';
                                            widgetB = '.widget-44b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[3]) {
                                            widgetA = '.widget-45a';
                                            widgetB = '.widget-45b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[4]) {
                                            widgetA = '.widget-46a';
                                            widgetB = '.widget-46b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[5]) {
                                            widgetA = '.widget-47a';
                                            widgetB = '.widget-47b';
                                            type_check = 'outbound';
                                        } else if (type == self.filter_list[6]) {
                                            widgetA = '.widget-48a';
                                            widgetB = '.widget-48b';
                                            type_check = 'outbound';
                                        } else if (type == self.filter_list[7]) {
                                            widgetA = '.widget-49a';
                                            widgetB = '.widget-49b';
                                            type_check = 'outbound';
                                        } else if (type == self.filter_list[8]) {
                                           widgetA = '.widget-50a';
                                            widgetB = '.widget-50b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[9]) {
                                            widgetA = '.widget-51a';
                                            widgetB = '.widget-51b';
                                            type_check = 'outbound';
                                        } else if (type == self.filter_list[10]) {
                                            widgetA = '.widget-52a';
                                            widgetB = '.widget-52b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[11]) {
                                            widgetA = '.widget-53a';
                                            widgetB = '.widget-53b';
                                            type_check = 'outbound';
                                        } else if (type == self.filter_list[12]) {
                                            widgetA = '.widget-54a';
                                            widgetB = '.widget-54b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[13]) {
                                            widgetA = '.widget-55a';
                                            widgetB = '.widget-55b';
                                            type_check = 'outbound';
                                        } else if (type == self.filter_list[14]) {
                                            widgetA = '.widget-56a';
                                            widgetB = '.widget-56b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[15]) {
                                            widgetA = '.widget-57a';
                                            widgetB = '.widget-57b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[16]) {
                                            widgetA = '.widget-58a';
                                            widgetB = '.widget-58b';
                                            type_check = 'inbound';
                                        } else if (type == self.filter_list[17]) {
                                            widgetA = '.widget-59a';
                                            widgetB = '.widget-59b';
                                            type_check = 'inbound';
                                        }

                                        if (self.voiceProjectType == 'inbound') {
                                            if(type_check == 'outbound') {
                                                $(widgetA).parent().hide();
                                            } else {
                                                $(widgetA).parent().show();    
                                            }
                                        }
                                        if (self.voiceProjectType == 'outbound') {
                                            if(type_check == 'inbound') {
                                                $(widgetA).parent().hide();
                                            } else {
                                                $(widgetA).parent().show();
                                            }
                                        }
                                        $(widgetA).addClass('widget-loader-show');
                                        $(widgetB).addClass('widget-data-hide');
                                        if (self.voiceProjectType == type_check) {
                                            $http({ method: "GET", url: voice_filter_ajax }).success(function(result) {
                                                self.voice_widget_function(result, type, widgetA, widgetB);
                                                self.highlightTypes(day_type, widgetB);
                                                self.voiceTypeFilter(self.voiceProjectType, 0);
                                            })
                                        }
                                    }
                                    if (self.voice_location != '') {
                                        self.location_value = $('#Location').val(self.voice_location);
                                        self.ajaxVoiceFilter(type, '');
                                    } else {
                                        self.LocationFilter.onchange = function () {
                                            self.locationValue = self.LocationFilter.value;
                                            voice_filter_calls();
                                            self.ajaxVoiceFilter(type, '');
                                        }
                                    }
                                    if (self.voice_skill != '') {
                                        self.skill_value = $('#Skill').val(self.voice_skill);
                                        self.ajaxVoiceFilter(type, '');
                                    } else {
                                        self.SkillFilter.onchange = function () {
                                            self.skillValue = self.SkillFilter.value;
                                            voice_filter_calls();
                                            self.ajaxVoiceFilter(type, '');
                                        }
                                    }
                                    if (self.voice_disposition != '') {
                                        self.disposition_value = $('#Disposition').val(self.voice_disposition);
                                        self.ajaxVoiceFilter(type, '');
                                    } else {
                                        self.DispositionFilter.onchange = function () {
                                            self.dispositionValue = self.DispositionFilter.value;
                                            voice_filter_calls();
                                            self.ajaxVoiceFilter(type, '');
                                        }
                                    }
                                    voice_filter_calls = function () {
                                        angular.forEach(self.filter_list, function(type) {
                                            self.ajaxVoiceFilter(type, '');
                                        });
                                    }
                                    voice_filter_calls();
                                }
                            } else {
                                angular.element(document.querySelector('#voice_filter_div')).addClass('hide');
                            }
                            self.hideLoading();
                        }

                    var packet_url = '/api/get_packet_details/?&project='+callback[3]+'&center='+callback[2]+'&from='+callback[0]+'&to='+callback[1]+'&voice_project_type='+self.voiceProjectType;

                    self.call_back = callback;
                    $http.get(packet_url).then(function(result){
                        $('#dropdown_title').html($(".brand_style").text().replace(" - DASHBOARD",''));
                        var sub_project_level = result.data.result.sub_project_level;
                        var sub_packet_level = result.data.result.sub_packet_level;
                        var work_packet_level = result.data.result.work_packet_level;
                        self.global_packet_values = result.data.result.fin;
                        self.drop_list = [];

                        self.top_employee_details =  result.data.result.top_five_employee_details;
                        self.top_five = result.data.resultonly_top_five;
                        self.volume_graphs = result.data.result.volumes_graphs_details;
                        self.drop_list =  result.data.result.drop_value;
                        self.sub_pro_sel = document.getElementById("0");
                        self.wor_pac_sel = document.getElementById("1");
                        self.sub_pac_sel = document.getElementById("2");

                        self.chartProcess(result);
                        $("#0, #1, #2").unbind("change");

                            if (result.data.result.fin.sub_project) {
                                console.log('sub_projet_exist');
                            }
                            else {   
                                $('#2').hide();
                                if (result.data.result.fin.work_packet) {
                                    console.log('work_packet_exist');
                                }
                                if (result.data.result.fin.sub_packet) {
                                    console.log('sub_packet_exist');
                                }
                                else {
                                    $('#1').hide();
                                }
                            }
                            if (result.data.result.fin.sub_packet) {
                                    console.log('sub_packet_exist');
                                }
                            else {
                                    $('#2').hide();
                              }   

                        for (var sub_pro in self.drop_list) {
                            self.sub_pro_sel.options[self.sub_pro_sel.options.length] = new Option(sub_pro, sub_pro);
                        }
                        if ( self.is_voice_flag == false) {
                            self.sub_pro_sel.onchange = function () {
                                self.wor_pac_sel.length = 1;
                                self.sub_pac_sel.length = 1;
                                if (this.selectedIndex < 1) {
                                    self.wor_pac_sel.options[0].text = "All"
                                    self.sub_pac_sel.options[0].text = "All"
                                    return;
                                }
                                self.wor_pac_sel.options[0].text = "All"
                                for (var wor_pac in self.drop_list[this.value]) {
                                    self.wor_pac_sel.options[self.wor_pac_sel.options.length] = new Option(wor_pac, wor_pac);
                                }
                                if (self.wor_pac_sel.options.length==2) {
                                    self.wor_pac_sel.onchange();
                                }
                            }
                            self.sub_pro_sel.onchange();
                            self.wor_pac_sel.onchange = function () {
                                self.sub_pac_sel.length = 1;
                                if (this.selectedIndex < 1) {
                                    self.sub_pac_sel.options[0].text = "All"
                                    return;
                                }
                                self.sub_pac_sel.options[0].text = "All"
                                var sub_pac = self.drop_list[self.sub_pro_sel.value][this.value];
                                for (var i = 0; i < sub_pac.length; i++) {
                                    self.sub_pac_sel.options[self.sub_pac_sel.options.length] = new Option(sub_pac[i], sub_pac[i]);
                                }
                                if (self.sub_pac_sel.options.length==2) {
                                    self.sub_pac_sel.selectedIndex=1;
                                    self.sub_pac_sel.onchange();
                                }
                                }
                        }
                self.drop_work_pack = 'All';
                self.drop_sub_proj = 'All';
                self.drop_sub_pack = 'All';

                if ((result.data.result.fin.sub_project) && (result.data.result.fin.work_packet)){
                $('#0').on('change', function(){
                    self.apply_class();   
                    self.add_loader();
                    self.drop_sub_proj = this.value;
                    self.drop_work_pack = self.wor_pac_sel.value;
                    self.drop_sub_pack = self.sub_pac_sel.value;
                    var dateEntered = document.getElementById('select').value
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    var placeholder = ''
                    self.call_back = [];
                    self.call_back.push(from);
                    self.call_back.push(to);                                                                                                                       var pro_cen_nam = $state.params.selpro;                                                                                                        self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                    var project_val = project_check.search('&');
                    if (project_val != -1) {
                        self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');    
                    }               
                    else {
                        self.project = pro_cen_nam.split('-')[1].replace(' ','');    
                    }
                    self.call_back.push(self.location);
                    self.call_back.push(self.project);
                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' +
                                            self.drop_work_pack;

                    self.main_widget_function(self.call_back, final_work);

                });

                $('#1').on('change', function(){
                    self.apply_class();
                    self.add_loader();
                    self.drop_sub_proj = self.sub_pro_sel.value;
                    self.drop_work_pack = this.value;
                    self.drop_sub_pack = self.sub_pac_sel.value;
                    var dateEntered = document.getElementById('select').value
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    var placeholder = ''
                    self.call_back = [];
                    self.call_back.push(from);
                    self.call_back.push(to);                                                                                                                       var pro_cen_nam = $state.params.selpro;                                                                                                        self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                    var project_val = project_check.search('&');
                    if (project_val != -1) {
                        self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');    
                    }
                    else {
                        self.project = pro_cen_nam.split('-')[1].replace(' ','');    
                    }
                    self.call_back.push(self.location);
                    self.call_back.push(self.project);

                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' +
                                            self.drop_work_pack;

                    self.main_widget_function(self.call_back, final_work);

                });

                $('#2').on('change', function(){
                    self.apply_class();
                    self.add_loader();
                    self.drop_work_pack = self.wor_pac_sel.value;
                    self.drop_sub_proj = self.sub_pro_sel.value;
                    self.drop_sub_pack = this.value;
                    var dateEntered = document.getElementById('select').value
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    var placeholder = ''
                    self.call_back = [];
                    self.call_back.push(from);
                    self.call_back.push(to);                                                                                                                       var pro_cen_nam = $state.params.selpro;                                                                                                        self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                    var project_val = project_check.search('&');
                    if (project_val != -1) {
                        self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');    
                    }
                    else {
                         self.project = pro_cen_nam.split('-')[1].replace(' ','');    
                    }
                    self.call_back.push(self.location);
                    self.call_back.push(self.project);

                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack;
                    self.main_widget_function(self.call_back, final_work);

                });

                }

                else {

                if ((result.data.result.fin.work_packet) && (result.data.result.fin.sub_packet)){

                $('#0').on('change', function(){

                    self.apply_class();                        
                    self.add_loader();
                    self.drop_work_pack = this.value;
                    self.drop_sub_proj = 'undefined';
                    self.drop_sub_pack = self.sub_pac_sel.value;
                    var dateEntered = document.getElementById('select').value
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    var placeholder = ''
                    self.call_back = [];
                    self.call_back.push(from);
                    self.call_back.push(to);                                                                                                                       var pro_cen_nam = $state.params.selpro;                                                                                                        self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                    var project_val = project_check.search('&');
                    if (project_val != -1) {
                        self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');    
                    }
                    else {
                         self.project = pro_cen_nam.split('-')[1].replace(' ','');    
                    }
                    self.call_back.push(self.location);
                    self.call_back.push(self.project);

                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack;
                    self.main_widget_function(self.call_back, final_work);

                });

                $('#1').on('change', function(){
                    self.apply_class();   
                    self.add_loader();
                    self.drop_sub_pack = this.value;
                    self.drop_sub_proj = 'undefined';
                    self.drop_work_pack;
                    var dateEntered = document.getElementById('select').value
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    var placeholder = ''
                    self.call_back = [];
                    self.call_back.push(from);
                    self.call_back.push(to);                                                                                                                               var pro_cen_nam = $state.params.selpro;                                                                                                                self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                   var project_val = project_check.search('&');
                    if (project_val != -1) {
                        self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');    
                    }
                    else {
                         self.project = pro_cen_nam.split('-')[1].replace(' ','');    
                    }
                    self.call_back.push(self.location);
                    self.call_back.push(self.project);

                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack;
                    self.main_widget_function(self.call_back, final_work);
                });
                }
                else {
                if (result.data.result.fin.work_packet){ 
                    $('#0').on('change', function(){ 
                        self.apply_class();
                        self.add_loader();
                        self.drop_work_pack = this.value;
                        self.drop_sub_proj = 'undefined';
                        self.drop_sub_pack = 'undefined';
                        var dateEntered = document.getElementById('select').value
                        dateEntered = dateEntered.replace(' to ','to');
                        var from = dateEntered.split('to')[0].replace(' ','');
                        var to = dateEntered.split('to')[1].replace(' ','');
                        var placeholder = '' 
                        self.call_back = [];
                        self.call_back.push(from);
                        self.call_back.push(to);
                        var pro_cen_nam = $state.params.selpro;                                                                                                        self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                        var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                        var project_val = project_check.search('&');
                        if (project_val != -1) {
                            self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');    
                        }
                        else {
                             self.project = pro_cen_nam.split('-')[1].replace(' ','');    
                        }
                        self.call_back.push(self.location);
                        self.call_back.push(self.project);

                        var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + 
                                            self.drop_work_pack;
                        self.main_widget_function(self.call_back, final_work);

                    });
                }
                }
                if (result.data.result.fin.sub_packet) {
                    $('#1').on('change', function(){

                    });
                }
                else {
                    self.drop_sub_pack = 'undefined';
                }
             }
                    
                if((self.work_packet != '') || (self.sub_packet != '') || (self.sub_project != '')) {
                    self.apply_class();
                    self.add_loader();
                    self.drop_sub_proj = self.sub_project;
                    self.drop_work_pack = self.work_packet;
                    self.drop_sub_pack = self.sub_packet;
                    var dateEntered = document.getElementById('select').value
                    dateEntered = dateEntered.replace(' to ','to');
                    var from = dateEntered.split('to')[0].replace(' ','');
                    var to = dateEntered.split('to')[1].replace(' ','');
                    var placeholder = ''
                    self.call_back = [];
                    self.call_back.push(from);
                    self.call_back.push(to);
                    var pro_cen_nam = $state.params.selpro;
                    self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    var project_check = pro_cen_nam.split('-')[1].replace(' ','');
                    var project_val = project_check.search('&');
                    if (project_val != -1) {
                        self.project = pro_cen_nam.split('-')[1].split('&')[0].replace(' ','');
                    }
                    else {
                        self.project = pro_cen_nam.split('-')[1].replace(' ','');
                    }
                    self.call_back.push(self.location);
                    self.call_back.push(self.project);

                    var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' +
                                                self.drop_work_pack;

                       self.main_widget_function(self.call_back, final_work);
                if ((self.drop_sub_proj == '') && (self.drop_work_pack != '') && (self.drop_sub_pack != '')) {
                    $('#0').val(self.drop_work_pack);
                    var x = document.getElementById('1');
                    var sub_packets = Object.keys(result.data.result.drop_value[self.drop_work_pack]);
                    for (var packet of sub_packets) {
                      var option = document.createElement('option');
                      option.text = packet;
                      x.add(option);
                    }
                  
                    $('#1').val(self.drop_sub_pack);

                } else if ((self.drop_sub_pack == '') && (self.drop_work_pack != '') && (self.drop_sub_proj == '')) {
                    //$('#0').val(self.drop_sub_proj);
                    $('#0').val(self.drop_work_pack);
                } else {
                    $('#0').val(self.drop_sub_proj);
                    var x = document.getElementById('1');
                    var work_packets = Object.keys(result.data.result.drop_value[self.drop_sub_proj]);
                    var sub_packets = result.data.result.drop_value[self.drop_sub_proj][self.drop_work_pack];
          
                    for (var packet of work_packets) {
                      var option = document.createElement('option');
                      option.text = packet;
                      x.add(option);
                    }

                    var y = document.getElementById('2');
                    for (var packet of sub_packets) {
                      var option = document.createElement('option');
                      option.text = packet;
                      y.add(option);
                    }
                    $('#1').val(self.drop_work_pack);
                    
                    $('#2').val(self.drop_sub_pack);
                    
                  }
                }           
                else {
                    self.main_widget_function(self.call_back, '');
                }
             })
             return callback;

            }).then(function(callback){

                self.dateType = function(key,all_data,name,button_clicked){

                self.call_back = callback;

                var obj = {
                    "self.chartOptions10":self.chartOptions10,
                    "self.chartOptions17":self.chartOptions17,
                    "self.chartOptions18":self.chartOptions18,
                    "self.chartOptions25":self.chartOptions25,
                    "self.chartOptions24":self.chartOptions24,
                    "self.chartOptions15":self.chartOptions15,
                    "self.chartOptions9":self.chartOptions9,
                    "self.chartOptions9_2":self.chartOptions9_2,
                    "self.chartOptions19":self.chartOptions19,
                    "self.chartOptions26":self.chartOptions26,
                    "self.chartOptions16":self.chartOptions16,
                    "self.chartOptions16_2":self.chartOptions16_2,
                    "self.chartOptions38":self.chartOptions38,
                    "self.chartOptions5":self.chartOptions5,
                    "self.chartOptions5_2":self.chartOptions5_2,
                    "self.chartOptions29":self.chartOptions29,
                   "self.chartOptions30":self.chartOptions30,
                    "self.chartOptions27":self.chartOptions27,
                    "self.chartOptions28":self.chartOptions28,
                    "self.chartOptions":self.chartOptions,
                    "self.chartOptions40":self.chartOptions40,
                    "self.chartOptions41":self.chartOptions41,
                    "self.chartOptions42":self.chartOptions42,
                    "self.chartOptions39":self.chartOptions39,
                    "self.chartOptions43":self.chartOptions43,
                    "self.chartOptions44":self.chartOptions44,
                    "self.chartOptions31":self.chartOptions31,
                    "self.chartOptions47":self.chartOptions47,
                    "self.chartOptions48":self.chartOptions48,
                    "self.chartOptions49":self.chartOptions49,
                    "self.chartOptions50":self.chartOptions50,
                    "self.chartOptions51":self.chartOptions51,
                    "self.chartOptions52":self.chartOptions52,
                    "self.chartOptions53":self.chartOptions53,
                    "self.chartOptions54":self.chartOptions54,
                    "self.chartOptions55":self.chartOptions55,
                    "self.chartOptions56":self.chartOptions56,
                    "self.chartOptions57":self.chartOptions57,
                    "self.chartOptions58":self.chartOptions58,
                    "self.chartOptions59":self.chartOptions59,
                    "self.chartOptions60":self.chartOptions60,
                    "self.chartOptions61":self.chartOptions61,
                    "self.chartOptions62":self.chartOptions62,
                    "self.chartOptions63":self.chartOptions63,
                    "self.chartOptions64":self.chartOptions64,
                    'self.chartOptions65':self.chartOptions65,
                    'self.chartOptions68':self.chartOptions68,
                    "self.chartOptions69":self.chartOptions69,
                    "self.chartOptions70":self.chartOptions70
                }

                self.render_data = obj[all_data];

                self.button_clicked = button_clicked;

                var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + 
                                  self.drop_work_pack + '&is_clicked=' + self.button_clicked;

                if ((name == 'chartOptions17') || (name == 'chartOptions18')) {

                    if (name == 'chartOptions17') {
                        $('.widget-17a').addClass('widget-loader-show');
                        $('.widget-17b').addClass('widget-data-hide');
                    }
                    if (name == 'chartOptions18') {
                        $('.widget-13a').addClass('widget-loader-show');
                        $('.widget-13b').addClass('widget-data-hide');
                    }
                    self.allo_and_comp(final_work, key, all_data); 
                }
                if ((name == 'chartOptions25') || (name == 'chartOptions15') || (name == 'chartOptions24')) {
                    if (name == 'chartOptions25') {
                        $('.widget-20a').addClass('widget-loader-show');
                        $('.widget-20b').addClass('widget-data-hide');
                    }
                    if (name == 'chartOptions24') {
                        $('.widget-19a').addClass('widget-loader-show');
                        $('.widget-19b').addClass('widget-data-hide');
                    }
                    if (name == 'chartOptions15') {
                        $('.widget-9a').addClass('widget-loader-show');
                        $('.widget-9b').addClass('widget-data-hide');
                    }
                    self.utill_all(final_work, key, all_data);
                }
                if (name == 'chartOptions19') {
                    $('.widget-14a').addClass('widget-loader-show');
                    $('.widget-14b').addClass('widget-data-hide');
                    self.productivity(final_work, key);
                }
                if (name == 'chartOptions38') {
                    $('.widget-33a').addClass('widget-loader-show');
                    $('.widget-33b').addClass('widget-data-hide');
                    self.prod_avg(final_work, key);
                }
                if (name == 'chartOptions31') {
                    $('.widget-26a').addClass('widget-loader-show');
                    $('.widget-26b').addClass('widget-data-hide');
                    self.tat_data(final_work, key);
                }

                if (name == 'chartOptions26') {
                    $('.widget-21a').addClass('widget-loader-show');
                    $('.widget-21b').addClass('widget-data-hide');
                    self.mont_volume(final_work, key);
                }
                
                if ((name == 'chartOptions16') || (name == 'chartOptions16_2')) {
                    if (name == 'chartOptions16') {
                        $('.widget-11a').addClass('widget-loader-show');
                        $('.widget-11b').addClass('widget-data-hide');
                    }
                    if (name == 'chartOptions16_2') {
                        $('.widget-12a').addClass('widget-loader-show');
                        $('.widget-12b').addClass('widget-data-hide');
                    }
                    self.fte_graphs(final_work, key, all_data);
                }
                if ((name == 'chartOptions10') || (name == 'chartOptions')) {
                    if (name == 'chartOptions10') {
                        $('.widget-6a').addClass('widget-loader-show');
                        $('.widget-6b').addClass('widget-data-hide');
                    }
                    if (name == 'chartOptions') {
                        $('.widget-1a').addClass('widget-loader-show');
                        $('.widget-1b').addClass('widget-data-hide');
                    }
                    self.main_prod(final_work, key, all_data);
                }

                if ((name == 'chartOptions9_2') || (name == 'chartOptions9')) {
                    if (name == 'chartOptions9') {
                       $('.widget-8a').addClass('widget-loader-show');
                       $('.widget-8b').addClass('widget-data-hide');        
                    }
                    if (name == 'chartOptions9_2') {
                    $('.widget-7a').addClass('widget-loader-show');
                    $('.widget-7b').addClass('widget-data-hide');
                    }
                        self.from_to(final_work, key, all_data);        
                }

                if (name == 'chartOptions40') {
                    $('.widget-35a').addClass('widget-loader-show');
                    $('.widget-35b').addClass('widget-data-hide');
                    self.pre_scan(final_work, key);
                }
                if (name == 'chartOptions42') {
                    $('.widget-37a').addClass('widget-loader-show');
                    $('.widget-37b').addClass('widget-data-hide');
                    self.nw_exce(final_work, key);
                }
                if (name == 'chartOptions41') {
                    $('.widget-36a').addClass('widget-loader-show');
                    $('.widget-36b').addClass('widget-data-hide');
                    self.overall_exce(final_work, key);
                }
                if (name == 'chartOptions39') {
                    $('.widget-34a').addClass('widget-loader-show');
                    $('.widget-34b').addClass('widget-data-hide');
                    self.upload_acc(final_work, key);
                }
                if (name == 'chartOptions65') {
                    $('.widget-60a').addClass('widget-loader-show');
                    $('.widget-60b').addClass('widget-data-hide');
                    self.aht_data(final_work, key);
                }
                if (name == 'chartOptions68') {
                    $('.widget-63a').addClass('widget-loader-show');
                    $('.widget-63b').addClass('widget-data-hide');
                    self.No_of_agents_AHT(final_work, key);
                }
                if (name == 'chartOptions69') {
                    $('.widget-64a').addClass('widget-loader-show');
                    $('.widget-64b').addClass('widget-data-hide');
                    self.Percentage_less_aht(final_work, key);
                }
                var chart_type_map = {};
                chart_type_map = { 'chartOptions47' : self.filter_list[0], 'chartOptions48' : self.filter_list[1] , 'chartOptions49' : self.filter_list[2], 'chartOptions50' : self.filter_list[3], 'chartOptions51' : self.filter_list[4], 'chartOptions52' : self.filter_list[5], 'chartOptions53' : self.filter_list[6], 'chartOptions54' : self.filter_list[7], 'chartOptions55' : self.filter_list[8], 'chartOptions56' : self.filter_list[9], 'chartOptions57' : self.filter_list[10], 'chartOptions58' : self.filter_list[11], 'chartOptions59': self.filter_list[12], 'chartOptions60': self.filter_list[13], 'chartOptions61': self.filter_list[14], 'chartOptions62': self.filter_list[15], 'chartOptions63': self.filter_list[16], 'chartOptions64': self.filter_list[17] };
                if( self.is_voice_flag ) {
                    if (name == 'chartOptions47' || name == 'chartOptions48' || name == 'chartOptions49' || name == 'chartOptions50' || name == 'chartOptions51' || name == 'chartOptions52' || name == 'chartOptions53' || name == 'chartOptions54' || name == 'chartOptions55' || name == 'chartOptions56' || name == 'chartOptions57' || name == 'chartOptions58' || name == 'chartOptions59' || name == 'chartOptions60' || name == 'chartOptions61' || name == 'chartOptions62' || name == 'chartOptions63' || name == 'chartOptions64') {
                            self.ajaxVoiceFilter(chart_type_map[name], key);
                        }
                    }
             }                    

             self.active_filters = function(key,button_clicked){
                self.button_clicked = button_clicked;
                var some = '' 
                if (key == 'day') { some = 'Day';}
                if (key == 'week') { some = 'Week';}
                if (key == 'month') { some = 'Month';}

                self.selected_date_type = some;

                if (self.selected_date_type === 'Week'){
                         $('.week2').addClass('active btn-success');
                         $('.week2').siblings().removeClass('active btn-success');
                  }
                if (self.selected_date_type === 'Month'){
                         $('.month2').addClass('active btn-success');
                         $('.month2').siblings().removeClass('active btn-success');
                 }
                if (self.selected_date_type === 'Day'){
                         $('.day2').addClass('active btn-success');
                         $('.day2').siblings().removeClass('active btn-success');
                 }

                var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack + '&is_clicked=' + self.button_clicked;

                if (self.button_clicked) {
                   if(self.is_voice_flag) {
                        self.day_type = key;
                        voice_filter_calls();
                    } else {
                
                        $('.widget-17a').addClass('widget-loader-show');    
                        $('.widget-17b').addClass('widget-data-hide');
                        $('.widget-13a').addClass('widget-loader-show');        
                        $('.widget-13b').addClass('widget-data-hide');

                        self.allo_and_comp(final_work, key);

                        $('.widget-20a').addClass('widget-loader-show');    
                        $('.widget-20b').addClass('widget-data-hide');
                        $('.widget-19a').addClass('widget-loader-show');    
                        $('.widget-19b').addClass('widget-data-hide');
                        $('.widget-9a').addClass('widget-loader-show');    
                        $('.widget-9b').addClass('widget-data-hide');

                        self.utill_all(final_work, key);

                        $('.widget-14a').addClass('widget-loader-show');     
                        $('.widget-14b').addClass('widget-data-hide');

                        self.productivity(final_work, key);

                        $('.widget-63a').addClass('widget-loader-show');     
                        $('.widget-63b').addClass('widget-data-hide');

                        self.No_of_agents_AHT(final_work, key);

                        $('.widget-64a').addClass('widget-loader-show');     
                        $('.widget-64b').addClass('widget-data-hide');

                        self.Percentage_less_aht(final_work, key);

                        $('.widget-33a').addClass('widget-loader-show');   
                        $('.widget-33b').addClass('widget-data-hide');

                        self.prod_avg(final_work, key);

                        $('.widget-26a').addClass('widget-loader-show');
                        $('.widget-2b').addClass('widget-data-hide');

                        self.tat_data(final_work, key);

                        
                        $('.widget-60a').addClass('widget-loader-show');
                        $('.widget-60b').addClass('widget-data-hide');
                    
                        self.aht_data(final_work, key);
            
                        $('.widget-21a').addClass('widget-loader-show');     
                        $('.widget-21b').addClass('widget-data-hide');

                        self.mont_volume(final_work, key);

                        $('.widget-11a').addClass('widget-loader-show');    
                        $('.widget-11b').addClass('widget-data-hide');
                        $('.widget-12a').addClass('widget-loader-show');   
                        $('.widget-12b').addClass('widget-data-hide');

                        self.fte_graphs(final_work, key);
         
                        $('.widget-6a').addClass('widget-loader-show');   
                        $('.widget-6b').addClass('widget-data-hide');
                        $('.widget-1a').addClass('widget-loader-show');   
                        $('.widget-1b').addClass('widget-data-hide');

                        self.main_prod(final_work, key);

                        $('.widget-8a').addClass('widget-loader-show');    
                        $('.widget-8b').addClass('widget-data-hide');
                        $('.widget-7a').addClass('widget-loader-show');   
                        $('.widget-7b').addClass('widget-data-hide');

                        self.from_to(final_work, key)

                        $('.widget-35a').addClass('widget-loader-show');    
                        $('.widget-35b').addClass('widget-data-hide');

                        self.pre_scan(final_work, key);

                        $('.widget-37a').addClass('widget-loader-show');   
                        $('.widget-37b').addClass('widget-data-hide');

                        self.nw_exce(final_work, key);

                        $('.widget-36a').addClass('widget-loader-show');   
                        $('.widget-36b').addClass('widget-data-hide');

                        self.overall_exce(final_work, key);

                        $('.widget-34a').addClass('widget-loader-show');   
                        $('.widget-34b').addClass('widget-data-hide');

                        self.upload_acc(final_work, key);
                    }
                }  
             }  
            })
                                
             var unWatch;

             this.$onInit = function () {
                unWatch = $scope.$watch(function(scope) {
                    return scope.options;
                },
                function(newVal){
                    if (newVal) {
                        $scope.radioModel = 'Day';
                        self.location = newVal.split(' - ')[0] + ' - ';
                        self.project = newVal.split(' - ')[1];
                        $('#0').show();
                        $('#1').show();
                        $('#2').show();

                        self.sub_pro_sel = document.getElementById("0");
                        self.removeOptions(self.sub_pro_sel);
                        self.wor_pac_sel = document.getElementById("1");
                        if (self.wor_pac_sel != null){
                            self.removeOptions(self.wor_pac_sel);
                        }
                        self.sub_pac_sel = document.getElementById("2");
                        if (self.sub_pac_sel != null){
                            self.removeOptions(self.sub_pac_sel);
                        }
                        var url_to_call = 'api/project/?name=' + newVal;
                        $http({method:"GET", url:url_to_call}).success(function(result){
                                                        
                            var pro_cen_nam = self.location + self.project.replace(' - ','');
                            self.useful_layout = [];
                            self.list_object = result.result.lay[0];
                            console.log('he');
                if((result.result.role === 'customer') || (result.result.role === 'team_lead') || (result.result.role === 'center_manager') || (result.result.role === 'nextwealth_manager'))
                {   
                    $('#emp_widget').hide();
                    $('#volume_table').hide();
                    self.first = result.result.dates.from_date;
                    
                    self.lastDate = self.first;
                    self.last = result.result.dates.to_date;
                    self.firstDate = self.last;
                    $('#select').val(self.first + ' to ' + self.last)

                    if ((result.result.role === 'customer') || (result.result.role === 'team_lead') || (result.result.role === 'nextwealth_manager') || (result.result.role === 'center_manager')){
                       $('#emp_widget').hide();
                        $('#volume_table').hide();
                       self.layout_list = result.result.lay[1].layout;
                    }
                    else {
                    $('#emp_widget').hide();
                    $('#volume_table').hide();
                        if (result.result.lay.length == 1){
                            self.layout_list = result.result.lay[0][pro_cen_nam]
                        }
                        else {
                            self.layout_list = result.result.lay[1][pro_cen_nam]
                        }
                    }
                    self.final_layout_values_list = {
                    'self.chartOptions':self.chartOptions,
                    'self.chartOptions4':self.chartOptions4,
                    'self.chartOptions6':self.chartOptions6,
                    'self.chartOptions9':self.chartOptions9,
                    'self.chartOptions9_2':self.chartOptions9_2,
                    'self.chartOptions10':self.chartOptions10,
                    'self.chartOptions15':self.chartOptions15,
                    'self.chartOptions15_2':self.chartOptions15_2,
                    'self.chartOptions16':self.chartOptions16,
                    'self.chartOptions16_2':self.chartOptions16_2,
                    'self.chartOptions17':self.chartOptions17,
                    'self.chartOptions18':self.chartOptions18,
                    'self.chartOptions5':self.chartOptions5,
                    'self.chartOptions5_2':self.chartOptions5_2,
                    'self.chartOptions19':self.chartOptions19,
                    'self.chartOptions20':self.chartOptions20,
                    'self.chartOptions21':self.chartOptions21,
                    'self.chartOptions22':self.chartOptions22,
                    'self.chartOptions23':self.chartOptions23,
                    'self.chartOptions24':self.chartOptions24,
                    'self.chartOptions25':self.chartOptions25,
                    'self.chartOptions26':self.chartOptions26,
                    'self.chartOptions27':self.chartOptions27,
                    'self.chartOptions28':self.chartOptions28,
                    'self.chartOptions29':self.chartOptions29,
                    'self.chartOptions30':self.chartOptions30,
                    'self.chartOptions31':self.chartOptions31,
                    'self.chartOptions32':self.chartOptions32,
                    'self.chartOptions33':self.chartOptions33,
                    'self.chartOptions34':self.chartOptions34,
                    'self.chartOptions35':self.chartOptions35,
                    'self.chartOptions36':self.chartOptions36,
                    'self.chartOptions37':self.chartOptions37,
                    'self.chartOptions38':self.chartOptions38,
                    'self.chartOptions39':self.chartOptions39,
                    'self.chartOptions40':self.chartOptions40,
                    'self.chartOptions41':self.chartOptions41,
                    'self.chartOptions42':self.chartOptions42,
                    'self.chartOptions43':self.chartOptions43,
                    'self.chartOptions44':self.chartOptios44,
                    'self.chartOptions45':self.chartOptions45,
                    'self.chartOptions46':self.chartOptions46,
                    'self.chartOptions47':self.chartOptions47,
                    'self.chartOptions48':self.chartOptions48,
                    'self.chartOptions49':self.chartOptions49,
                    'self.chartOptions50':self.chartOptions50,
                    'self.chartOptions51':self.chartOptions51,
                    'self.chartOptions52':self.chartOptions52,
                    "self.chartOptions53":self.chartOptions53,
                    "self.chartOptions54":self.chartOptions54,
                    "self.chartOptions55":self.chartOptions55,
                    "self.chartOptions56":self.chartOptions56,
                    "self.chartOptions57":self.chartOptions57,
                    "self.chartOptions58":self.chartOptions58,
                    "self.chartOptions59":self.chartOptions59,
                    "self.chartOptions60":self.chartOptions60,
                    "self.chartOptions61":self.chartOptions61,
                    "self.chartOptions62":self.chartOptions62,
                    "self.chartOptions63":self.chartOptions63,
                    "self.chartOptions64":self.chartOptions64,
                    'self.chartOptions65':self.chartOptions65,
                    };
                    var final_layout_list = [];
                    for (var single in self.layout_list){
                        for (var double in self.list_object){
                            if (self.layout_list[single] === double) {
                                final_layout_list.push(self.list_object[double])
                            }
                        }
                    }

                    var is_filled = 0;
                    var col_size = 0;
                    var first_row = [];
                    var second_row = [];
                    for (var one_lay in final_layout_list){
                        col_size = col_size + final_layout_list[one_lay].col;
                        if (col_size > 12){
                            is_filled = 1;
                            if (col_size >= 12){
                                col_size = 0;
                            }
                        }
                        if (is_filled){
                            second_row.push(final_layout_list[one_lay]);
                        }
                        else{
                            first_row.push(final_layout_list[one_lay]);
                        }
                        if ((col_size%12 == 0) | (col_size > 12)){
                            is_filled = 1;
                            if (col_size >= 12){
                                col_size = 0;
                            }
                        }
                    }
                    self.useful_layout.push(first_row,second_row);

                    self.location = pro_cen_nam.split('-')[0].replace(' ','') + ' - '
                    self.project = pro_cen_nam.split('-')[1].replace(' ','')
                    var from_to_data = from_to + 'from=' + self.lastDate + '&to=' + self.firstDate + '&project=' + self.project
                              + '&center=' + self.location  + '&type=' + self.day_type;
                }
                            self.first = result.result.dates.from_date;
                            self.lastDate = self.first;
                            self.last = result.result.dates.to_date;
                            self.firstDate = self.last;
                        $('#select').val(self.first + ' to ' + self.last)
                        $("#0").append(new Option("All"));
                        $("#1").append(new Option("All"));
                        $("#2").append(new Option("All"));
                        $('.day').addClass('active btn-success');
                        $('.day').siblings().removeClass('active btn-success');
                        if (self.project == "Wallmart - "){
                            var from_to_data = from_to + 'from=' + self.lastDate + '&to=' + self.firstDate + '&project=' + 'DellBilling - ' +
                                 '&center=' + 'Salem' + '&type=' + self.day_type;
                        }
                        else
                        {
                         var from_to_data = from_to + 'from=' + self.lastDate + '&to=' + self.firstDate + '&project=' + self.project +
                             '&center=' + self.location + '&type=' + 'day';
                        }
                        self.tabData.state = JSON.parse("{}");

                        var static_ajax = static_data + '&project=' + self.project + '&center=' + self.location
                        self.main_render(from_to_data)
                        $http({method:"GET", url:static_ajax}).success(function(result){
                           self.static_widget_render(result,self.project,self.location);

                            $('.widget-27a').removeClass('widget-loader-show');
                            $('.widget-27b').removeClass('widget-data-hide');
                            $('.widget-30a').removeClass('widget-loader-show');
                            $('.widget-30b').removeClass('widget-data-hide');
                            $('.widget-28a').removeClass('widget-loader-show');
                            $('.widget-28b').removeClass('widget-data-hide');
                            $('.widget-27a').removeClass('widget-loader-show');
                            $('.widget-27b').removeClass('widget-data-hide');
                            $('.widget-29a').removeClass('widget-loader-show');
                            $('.widget-29b').removeClass('widget-data-hide');
                            $('.widget-31a').removeClass('widget-loader-show');
                            $('.widget-31b').removeClass('widget-data-hide');
                            $('.widget-32a').removeClass('widget-loader-show');
                            $('.widget-32b').removeClass('widget-data-hide');

                            });
                        });
                    }
                });
             };
             this.$onDestroy = function () {
               return unWatch && unWatch();
             }
             var from_to_data = from_to + 'from=' + self.lastDate + '&to=' + self.firstDate + '&project=' + self.project + '&center=' + self.location;

                self.last = self.firstDate;
                self.first = self.lastDate;
 
            self.get_date = function(){
                var dateEntered = document.getElementById('select').value;
                dateEntered = dateEntered.replace(' to ','to');
                var from = dateEntered.split('to')[0].replace(' ','');
                var to = dateEntered.split('to')[1].replace(' ','');
                return [from,to];
            };

            $http({method:"GET", url:drop_down_link}).success(function(result){
                angular.extend(self.packet_hierarchy_list, result.result.level);
             })

              self.chartOptions = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                lang: {
                   thousandsSep: ','
                },
                yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: '',

                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
               credits: {
                enabled: false
               },
            };
      
           self.chartOptions39 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
               },
               tooltip: {
                    valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

           self.chartOptions40 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
               },

               tooltip: {
                    valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

           self.chartOptions41 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
               },

               tooltip: {
                    valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions42 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
               },

               tooltip: {
                    valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

           self.chartOptions38 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                lang: {
                   thousandsSeparator: ','
                },
                yAxis: {
                gridLineColor: 'a2a2a2',

                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify',

                }
               },
               tooltip: {
                valueSuffix: '',

                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
               credits: {
                enabled: false
               },
            }; 
            self.chartOptions10 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: '',

                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               }    
            };

            self.chartOptions68 = {
                chart : {
                 type: 'column',
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },

               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions69 = {
                chart : {
                 type: 'column',
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },

               tooltip: {
                valueSuffix: ' %'
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions9 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },

               tooltip: {
                valueSuffix: ' %'
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions9_2 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },

               tooltip: {
                valueSuffix: ' %'
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions4 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                type: 'category'
            },
            legend: {
                enabled: false
            },
            yAxis: {
                min:'',
                max:'',
                gridLineColor: 'a2a2a2',
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: ' %',
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                point: {
                    events:{
                    }
                },
                dataLabels: {
                enabled: true,
                format: '{y} %',
                valueDecimals: 2
                }
                }
            },
            };

            self.chartOptions43 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                type: 'category'
            },
            legend: {
                enabled: false
            },
            yAxis: {
                min:'',
                max:'',
                gridLineColor: 'a2a2a2',
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: ' %',
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                point: {
                    events:{
                    }
                },
                dataLabels: {
                enabled: true,
                format: '{y} %',
                valueDecimals: 2
                }
                }
            },
            };

          self.chartOptions44 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                type: 'category'
            },
            legend: {
                enabled: false
            },
            yAxis: {
                min:'',
                max:'',
                gridLineColor: 'a2a2a2',
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: ' %',
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                point: {
                    events:{
                    }
                },
                dataLabels: {
                enabled: true,
                format: '{y} %',
                valueDecimals: 2
                }
                }
             },
            };

            self.chartOptions45 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#696969'
                               }
                            }
                        }
                    },
                };

            self.chartOptions46 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                   pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#696969'
                               }
                            }
                        }
                    },
                };

        self.chartOptions47 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },   
            title: {
                text: ''
            },   
            subtitle: {
                text: ''
            },   
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },   
            tooltip: {
                valueSuffix: '',

                formatter: function () { 
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },   
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    cursor: 'pointer',
                point: {
                    events:{
                    }
                }
                }
            }
            };

            self.chartOptions48 = {
                chart: {
                    type: 'column',
                    backgroundColor: "transparent",
                    reflow: false
                 },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                tooltip: {
                    valueSuffix: '',

                    formatter: function () {
                                 return "<small>" + this.x + "</small><br/>" +
                                        "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                               }
                   },
                plotOptions:{
                    series:{
                        allowPointSelect: true,
                        cursor: 'pointer',
                    point: {
                        events:{
                        }
                    }
                    }
                }
            };

            self.chartOptions50 = {
                chart: {
                    type: 'column',
                    backgroundColor: "transparent",
                    reflow: false
                },
                title: {
                    text: ''
                 },
                subtitle: {
                    text: ''
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                    reversedStacks: false,
                    title: {
                        text: ''
                    },
                    stackLabels: {
                        enabled: true,
                            style: {
                                fontWeight: 'bold',
                                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                            }
                    }

                },
                tooltip: {
                    valueSuffix: '',
                    /*formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }*/
                    headerFormat: '<b>{point.x}</b><br/>',
                    //pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
                  pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                  shared: true
               },
                plotOptions:{
                    column: {
                        stacking: 'percent',
                        dataLabels: {
                            enabled: true,
                            color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                        }
                    }
                }
            };

            self.chartOptions49 = {
                chart: {
                    type: 'column',
                    backgroundColor: "transparent",
                    reflow: false
                },   
                title: {
                    text: ''
                 },   
                subtitle: {
                    text: ''
                },   
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                    title: {
                        text: ''
                    }
                },   
                tooltip: {
                    valueSuffix: '',
                    formatter: function () { 
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },   
                plotOptions: {
                    column: {
                        stacking: 'normal',
                        dataLabels: {
                            enabled: true,
                            color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
                        }
                    }
                }
            };
    
            self.chartOptions51 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#696969'
                               }
                            }
                        }
                 },
            };

            self.chartOptions52 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#696969'
                               }
                            }
                        }
                    },
            };

            self.chartOptions53 = {
                chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },    
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },     
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: '',

                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },  
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    cursor: 'pointer',
                point: {   
                    events:{
                    }
                }
                }
            }
            };


            self.chartOptions54 = {
                chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: '',

                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    cursor: 'pointer',
                point: {
                    events:{
                    }
                }
                }
            }
            };

            self.chartOptions55 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };


            self.chartOptions56 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },  
                               yAxis: {
                gridLineColor: 'a2a2a2',
               min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: { 
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions57 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions58 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };


            self.chartOptions59 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions60 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions61 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions62 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };


            self.chartOptions63 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

self.chartOptions64 = {
                chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{
            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Logged in',
                color:'a2a2a2',
            },
            opposite: true
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Calls',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
        }, { // Teritary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Required',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            plotLines: [{
                color: '#1919ff',
                dashStyle: 'shortdash',
                width: 3,
                zIndex: 10
            }],
            opposite: true        
        
        }],
        tooltip: {
            shared: true
        },
        legend: {
               itemStyle: {
                    'color' : '#717171',
               }
        },
    }

            self.chartOptions5 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#696969'
                               }
                            }
                        }
                    },
                };

            self.chartOptions23 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                   pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#EEE'
                               }
                            }
                        }
                    },
                };

            self.chartOptions5_2 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie',
                    reflow: false
                  },
                title: {
                    text: ''
                  },
                tooltip: {
                    pointFormat: '<b>{point.y}</b>'
                  },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        point: {
                           events:{
                           }
                        },
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.y} ',
                            style: {
                                color:(Highcharts.theme && Highcharts.theme.background2) || '#696969'
                               }
                            }
                        }
                    },
                };
            self.chartOptions6 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                type: 'category'
            },
            legend: {
                enabled: false
            },
            yAxis: {
                min:'',
                max:'',
                gridLineColor: 'a2a2a2',
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: ' %',
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                point: {
                    events:{
                    }
                },
                dataLabels: {
                    enabled: true,
                    format: '{y} %',
                    valueDecimals: 2
                }
                }
            },
            };
            self.chartOptions15 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions24 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions26 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                yAxis: {
                    gridLineColor: 'a2a2a2',
                    min: 0,
                    title: {
                        text: '',
                        align: 'high'
                    },
                    labels: {
                    overflow: 'justify'
                    }
                },
                tooltip: {
                    valueSuffix: '',
                    formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           } 
                },
                credits: {
                    enabled: false
                },
            };

        self.chartOptions27 = {
            chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{
            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Cumulative %',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            plotLines: [{
                color: '#89A54E',
                dashStyle: 'shortdash',
                value: 80,
                width: 3,
                zIndex: 10
            }], 
            opposite: true
        },],
        tooltip: {
            shared: true
        },
        legend: {
              itemStyle: {
                    'color' : '#717171',
               }
        },
    }
            
        self.chartOptions28 = {
            chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{

            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Cumulative %',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            plotLines: [{
                color: '#89A54E',
                dashStyle: 'shortdash',
                value: 80,
                width: 3,
                zIndex: 10
            }], 
            opposite: true
        },],
        tooltip: {
            shared: true
        },
        legend: {
              itemStyle: {
                    'color' : '#717171',
               }
        },
    }
            
        self.chartOptions29 = {
            chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{
            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Cumulative %',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            plotLines: [{
                color: '#89A54E',
                dashStyle: 'shortdash',
                value: 80,
                width: 3,
                zIndex: 10
            }], 
            opposite: true
        },],
        tooltip: {
            shared: true
        },
        legend: {
              itemStyle: {
                    'color' : '#717171',
               }
        },
    }

        self.chartOptions31 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            }; 

        self.chartOptions30 = {
            chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{
            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Cumulative %',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            plotLines: [{
                color: '#89A54E',
                dashStyle: 'shortdash',
                value: 80,
                width: 3,
                zIndex: 10
            }],
            opposite: true
        },],
        tooltip: {
            shared: true
        },
        legend: {
              itemStyle: {
                    'color' : '#717171',
               }
        },
    }

            self.chartOptions25 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },

               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions16 = {
                chart : {
                 backgroundColor: "transparent",
                reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify',
                }
               },
               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };
            self.chartOptions16_2 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false,
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify',
                }
               },
               tooltip: {
                valueSuffix: ''
               }, 
                plotOptions : {
                series : {
                    dataLabels: {
                        enabled: true
                    }
                }
            },
               credits: {
                enabled: false
               },
            };

            self.chartOptions17 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            tooltip: {
                valueSuffix: '',

                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    showInLegend: false,
                    cursor: 'pointer',
                point: {
                    events:{
                    }
                }
                }
            }
            };

            self.chartOptions18 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },
               tooltip: {
                valueSuffix: '',
                
                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions19 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                               yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify'
                }
               },

               tooltip: {
                valueSuffix: ''
               },
               credits: {
                enabled: false
               },
            };

            self.chartOptions20 = {
                chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{
            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Error Accuracy',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Error Count',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            opposite: true
        },],
        tooltip: {
            shared: true
        },
        legend: {
              itemStyle: {
                    'color' : '#717171',
               } 
        },
    }

    self.chartOptions21 = {
                chart: {
            zoomType: 'xy',
            backgroundColor: "transparent",
            reflow: false
        },
        xAxis: [{
            crosshair: true,
            color:'a2a2a2',
        }],
        yAxis: [{
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            gridLineColor: 'a2a2a2',
            labels: {
                color: 'a2a2a2',
                format: '{value}',
            },
            title: {
                text: 'Error Accuracy',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Error Count',
                color:'a2a2a2',
            },
            labels: {
                color: 'a2a2a2',
                format: '{value} ',
            },
            opposite: true
        },],
        tooltip: {
            shared: true
        },
        legend: {
               itemStyle: {
                    'color' : '#717171',
               }
        },
    }

   self.chartOptions32 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                lang: {
                   thousandsSeparator: ','
                },
                yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify',
                }
               },
               tooltip: {
                valueSuffix: '',
                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
               credits: {
                enabled: false
               },
            };

    self.chartOptions33 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                lang: {
                   thousandsSeparator: ','
                },
                yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify',

                }
               },
               tooltip: {
                valueSuffix: '',
                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },

               credits: {
                enabled: false
               },
           };

    self.chartOptions34 = {
                chart : {
                 backgroundColor: "transparent",
                 reflow: false
                },
                lang: {
                   thousandsSeparator: ','
                },
                yAxis: {
                gridLineColor: 'a2a2a2',

                min: 0,
                title: {
                 text: '',
                 align: 'high'
                },
                labels: {
                 overflow: 'justify',

                }
               },
               tooltip: {
                valueSuffix: '',
                formatter: function () {
                             return "<small>" + this.x + "</small><br/>" +
                                    "<b>" + this.series.name + "</b> : " + Highcharts.numberFormat(this.y, null, null, ",");
                           }
               },
               credits: {
                enabled: false
               },
            };

    self.chartOptions35 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    cursor: 'pointer',
                point: {
                    events:{
                    }
                }
                }
            }
         };

    self.chartOptions36 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    cursor: 'pointer',
                point: {
                    events:{
                    }
                }
                }
            }
         };         

    self.chartOptions37 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent",
                reflow: false
             },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: ''
                }
            },
            plotOptions:{
                series:{
                    allowPointSelect: true,
                    cursor: 'pointer',
                point: {
                    events:{
                    }
                }
                }
            }
         };

        self.chartOptions65 = {
            chart : {
                backgroundColor: "transparent",
                reflow: false
            },
            lang: {
               thousandsSep: ','
            },
            yAxis: {
                gridLineColor: 'a2a2a2',
                min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }   
           },
           tooltip: {
               valueSuffix: '',
           },
           credits: {
               enabled: false
           },
        };


    Highcharts.Pointer.prototype.onContainerMouseDown = function (e) {
            e = this.normalize(e);
                this.dragStart(e);
    };

            self.names;
            self.names_2;
            self.first;
            self.last;
            self.location = '';
            self.project = '';
            self.packet_count = '';
            self.list_object = '';
            self.layout_list = '';
            self.packet_hierarchy_list = [];
            self.day_type = 'day';
            self.useful_layout = [];
            self.sel_pack = [];
            self.drop_list = [];
            self.top_employee_details = '';
            self.global_packet_values = '';
            self.firstDate;
            self.lastDate;
            self.start;
            self.end;
            self.voice_filters = {};
            self.voice_filters['Location'] = [];
            self.voice_filters['Skill'] = [];
            self.voice_filters['Disposition'] = [];
            self.voiceProjectType = 'inbound';
            self.voiceProjectList = [];
            self.voiceTypeFilter;
            self.is_voice_flag = false;
            self.locationValue;
            self.skillValue;
            self.dispositionValue;
            }],

            "bindings": {
              "hideLoading": "&",
              "showLoading": "&",
              "updateState": "&",
              "selectedValue": "=",
              "selectDropdown": "&",
              "tabData": "<"
            }
         });

}(window.angular));
