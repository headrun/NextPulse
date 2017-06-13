;(function (angular) {
  "use strict";

  var Annotation = buzz_data.Annotation;

  angular.module("page1")
         .component("page1", {

           "templateUrl": "/js/page1/page1.html",
           "controller": ['$http','$scope','$rootScope', '$state', 

           function ($http,$scope,$rootScope,$state) {
             var self = this;
             var color = $rootScope.color;
             var from_to = '/api/from_to/?'
             var static_data = '/api/static_production_data/?'
             var error_api = '/api/error_board'
             var def_disp = '/api/default'
             var project_dropdown_count = '/api/dropdown_data_types/?'
             var yesterdays_data = '/api/yesterdays_data'
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
             self.project_live = ''
             self.center_live = ''

             //self.sell_proo = $state.params.selpro;
             $scope.singleModel = 1; 

             $scope.radioModel = 'Day';

             $scope.checkModel = {
                day: true,
                week: false,
                month: false
             };

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
                callback.push.apply(callback, [self.start, self.end, self.center_live, self.project_live])
                self.main_widget_function(callback,'');
               });

             /*self.dateType = function(key,all_data,name,button_clicked){

                var obj = {
                    "self.chartOptions17":self.chartOptions17,
                    "self.chartOptions18":self.chartOptions18,
                    "self.chartOptions25":self.chartOptions25,
                    "self.chartOptions24":self.chartOptions24,
                    "self.chartOptions15":self.chartOptions15,
                    "self.chartOptions9":self.chartOptions9,
                    "self.chartOptions9_2":self.chartOptions9_2,
                }

                self.render_data = obj[all_data];
                self.button_clicked = button_clicked;
             }*/

             /*self.allo_and_comp = function() {

                $http({method:"GET", url: allo_and_comp}).success(function(result){

                    angular.extend(self.chartOptions17, {
                        xAxis: {
                            categories: result.result.date,
                        },
                        series: result.result.bar_data
                    });

                    angular.extend(self.chartOptions18, {
                        xAxis: {
                            categories: result.result.date,
                        },
                        series: result.result.line_data
                    });
                })
             }*/


             self.main_widget_function = function(callback, packet) {
                        
                    self.center_live = callback[2];

                    self.project_live = callback[3];

                    //self.lastDate+'&to='+self.firstDate+'&type=' + self.day_type;

                    self.data_to_show = '?&project='+callback[3]+'&center='+callback[2]+'&from='+ callback[0]+'&to='+ callback[1]+packet+'&type=';
                    self.common_for_all = self.data_to_show + self.day_type;
                    //var allo_and_comp = '/api/alloc_and_compl/'+self.common_for_all;
                    var utill_all = '/api/utilisation_all/'+self.common_for_all;
                    var erro_all = '/api/erro_data_all/'+self.common_for_all;
                    var productivity = '/api/productivity/'+self.common_for_all;
                    var mont_volume = '/api/monthly_volume'+self.common_for_all;

                    self.allo_and_comp = function(final_work, type) {

                        if (type == undefined) {
                            type = 'day'
                        }

                        if (final_work == undefined) {
                            final_work = ''
                        }

                        self.type = type;

                        var allo_and_comp = '/api/alloc_and_compl/'+self.data_to_show + type + final_work;

                        $http({method:"GET", url: allo_and_comp}).success(function(result){

                            if (self.type == 'day') {
                                var date_list = result.result.date;
                                var data_list_bar = result.result.bar_data;
                                var data_list_line = result.result.line_data;
                            }

                            if (self.type == 'week') {
                                var date_list = result.result.date_week;
                                var data_list_bar = result.result.volume_graphs.bar_data;
                                var data_list_line = result.result.volume_graphs.line_data;
                            }

                            angular.extend(self.chartOptions17, {
                                xAxis: {
                                    categories: date_list,
                                },
                                series: data_list_bar
                            });

                            angular.extend(self.chartOptions18, {
                                xAxis: {
                                    categories: date_list,
                                },
                                series: data_list_line
                            });
                        })
                    }

                    self.allo_and_comp(undefined, undefined);

                    $http({method:"GET", url: utill_all}).success(function(result){

                            angular.extend(self.chartOptions25, {
                                xAxis: {
                                    categories: result.result.date,
                                },
                                series: result.result.utilization_operational_details
                            });

                            angular.extend(self.chartOptions24, {
                                xAxis: {
                                    categories: result.result.date,
                                },
                                series: result.result.utilization_fte_details
                            });

                            angular.extend(self.chartOptions15, {
                                xAxis: {
                                    categories: result.result.date,
                                },
                                series: result.result.original_utilization_graph
                            });

                        })

                       $http({method:"GET", url: productivity}).success(function(result){

                            angular.extend(self.chartOptions19, {
                                xAxis: {
                                    categories: result.result.date,
                                },
                                series: result.result.result.result.original_productivity_graph
                            });

                        })

                       $http({method:"GET", url: mont_volume}).success(function(result){

                            debugger;

                       })

                       $http({method:"GET", url: erro_all}).success(function(result){

                            angular.extend(self.chartOptions9, {
                                xAxis: {
                                    categories: result.result.date,
                                },
                                series: result.result.external_time_line
                            });

                            angular.extend(self.chartOptions9_2, {
                                xAxis: {
                                    categories: result.result.date,
                                },
                                series: result.result.internal_time_line
                            });

                            angular.extend(self.chartOptions4.yAxis,{
                                min:result.result.ext_min_value,
                                max:result.result.ext_max_value
                            });

                           angular.extend(self.chartOptions4,{
                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.internal_accuracy_graph
                               }]
                           }); 

                            angular.extend(self.chartOptions6.yAxis,{
                                min:result.result.ext_min_value,
                                max:result.result.ext_max_value
                            });

                           angular.extend(self.chartOptions6,{
                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.external_accuracy_graph
                               }]
                           });


               self.hideLoading();
                }) 
            }
             /*self.allo_and_comp = function() {

                $http({method:"GET", url: allo_and_comp}).success(function(result){

                    angular.extend(self.chartOptions17, {
                        xAxis: {
                            categories: result.result.date,
                        },
                        series: result.result.bar_data
                    });

                    angular.extend(self.chartOptions18, {
                        xAxis: {
                            categories: result.result.date,
                        },  
                        series: result.result.line_data
                    }); 
                })  
             }*/

             $http.get(self.pro_landing_url).then(function(result){

                self.list_object = result.data.result.lay[0];
                self.layout_list = result.data.result.lay[1].layout;

                var pro_cen_nam = $state.params.selpro;                                                                                           
                self.call_back = [];

                self.first = result.data.result.dates.from_date;                                                                                       
                self.last = result.data.result.dates.to_date;

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
                    'self.chartOptions46':self.chartOptions46
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
                self.project = pro_cen_nam.split('-')[1].replace(' ','') + ' - '
                
                self.call_back.push(self.location);
                self.call_back.push(self.project);
             
                return self.call_back;

           }).then(function(callback){
                    var packet_url = '/api/get_packet_details/?&project='+callback[3]+'&center='+callback[2]+'&from='+'2017-01-09'+'&to='+'2017-01-15';
                    self.call_back = callback;
                    $http.get(packet_url).then(function(result){
                        $('#dropdown_title').html($(".brand_style").text().replace(" - DASHBOARD",''));
                        var sub_project_level = result.data.result.sub_project_level;
                        var sub_packet_level = result.data.result.sub_packet_level;
                        var work_packet_level = result.data.result.work_packet_level;
                        self.global_packet_values = result.data.result.fin;
                        self.drop_list = [];

                        self.top_employee_details =  result.data.result.top_five_employee_details;
                        self.top_five = result.data.result.only_top_five;
                        self.volume_graphs = result.data.result.volumes_graphs_details;
                        self.drop_list =  result.data.result.drop_value;
                        self.sub_pro_sel = document.getElementById("0");
                        self.wor_pac_sel = document.getElementById("1");
                        self.sub_pac_sel = document.getElementById("2");


                        $("#0, #1, #2").unbind("change");

                            if (result.data.result.fin.sub_project) {
                                console.log('sub_projet_exist');
                            }
                            else {   
                                $('#2').hide();
                                //$('#2').remove();
                                if (result.data.result.fin.work_packet) {
                                    console.log('work_packet_exist');
                                }
                                if (result.data.result.fin.sub_packet) {
                                    console.log('sub_packet_exist');
                                }
                                else {
                                    $('#1').hide();
                                    //$('#1').remove();
                                }
                            }

                            if (result.data.result.fin.sub_packet) {
                                    console.log('sub_packet_exist');
                                }
                            else {
                                    $('#2').hide();
                                    //$('#1').remove();
                              }


                        for (var sub_pro in self.drop_list) {
                            self.sub_pro_sel.options[self.sub_pro_sel.options.length] = new Option(sub_pro, sub_pro);
                        }
                if ((result.data.result.fin.sub_project) && (result.data.result.fin.work_packet)){

                $('#0').on('change', function(){

                });

                $('#1').on('change', function(){

                });

                $('#2').on('change', function(){

                });

                }

                else {

                if ((result.data.result.fin.work_packet) && (result.data.result.fin.sub_packet)){

                $('#0').on('change', function(){

                });

                }

                else {

                if (result.data.result.fin.work_packet){ 

                    $('#0').on('change', function(){ 
                        self.drop_work_pack = this.value;
                        self.drop_sub_proj = 'undefined';
                        self.drop_sub_pack = self.sub_pac_sel.value;
                        
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

                    })
                    return callback;
           }).then(function(callback){
                    var final_work = '';
                    self.main_widget_function(callback, final_work);
                    return callback;

            }).then(function(callback){

                self.dateType = function(key,all_data,name,button_clicked){

                self.call_back = callback;

                
                var obj = {
                    "self.chartOptions17":self.chartOptions17,
                    "self.chartOptions18":self.chartOptions18,
                    "self.chartOptions25":self.chartOptions25,
                    "self.chartOptions24":self.chartOptions24,
                    "self.chartOptions15":self.chartOptions15,
                    "self.chartOptions9":self.chartOptions9,
                    "self.chartOptions9_2":self.chartOptions9_2,
                    "self.chartOptions19":self.chartOptions19,
                    "self.chartOptions26":self.chartOptions26,
                }

                self.render_data = obj[all_data];

                self.button_clicked = button_clicked;

                var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + 
                                  self.drop_work_pack + '&is_clicked=' + self.button_clicked;

                //self.main_widget_function(self.call_back, final_work);

                /*var common_for_all = '?&project='+callback[3]+'&center='+callback[2]+'&from='+'2017-01-09'+'&to='+'2017-01-15'+'&type=' +
                                     self.day_type + packet;
                var allo_and_comp = '/api/alloc_and_compl/'+common_for_all;*/

                self.allo_and_comp(final_work, key);

             }                    
            })
                            /*if ((result.result.fin.sub_project) && (result.result.fin.work_packet)){
                                $('#0').on('change', function(){
                                            if (self.day_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.day_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }

                                            if (self.day_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }
                                    self.showLoading();
                                    self.drop_sub_proj = this.value;
                                    self.drop_work_pack = self.wor_pac_sel.value;
                                    self.drop_sub_pack = self.sub_pac_sel.value;
                        //$('.day').addClass('active');
                        //$('.day').siblings().removeClass('active');


                            var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack +
                                '&work_packet=' + self.drop_work_pack
                            var dateEntered = document.getElementById('select').value
                            dateEntered = dateEntered.replace(' to ','to');
                            var from = dateEntered.split('to')[0].replace(' ','');
                            var to = dateEntered.split('to')[1].replace(' ','');
                            var placeholder = ''*/
                            /*var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                                    + '&center=' + self.location + '&type=' + self.day_type  + final_work;*/
                            /*var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                                    + '&center=' + self.location + '&type=' + 'day'  + final_work;
                            $http({method:"GET", url:from_to_data}).success(function(result){
                                self.chart_render(result,self.project,self.location);
                            });
                                });
                                $('#1').on('change', function(){
                                            if (self.day_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.day_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }

                                            if (self.day_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }
                                    self.showLoading();
                                    self.drop_sub_proj = self.sub_pro_sel.value
                                    self.drop_work_pack = this.value;
                                    self.drop_sub_pack = self.sub_pac_sel.value;

                            var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack +
                                '&work_packet=' + self.drop_work_pack
                            var dateEntered = document.getElementById('select').value
                            dateEntered = dateEntered.replace(' to ','to');
                            var from = dateEntered.split('to')[0].replace(' ','');
                            var to = dateEntered.split('to')[1].replace(' ','');
                            var placeholder = ''
                            var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                                    + '&center=' + self.location + '&type=' + 'day'  + final_work;
                            $http({method:"GET", url:from_to_data}).success(function(result){
                                self.chart_render(result,self.project,self.location);
                            });
                                });
                                    $('#2').on('change', function(){
                                            if (self.day_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.day_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }

                                            if (self.day_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }
                                        self.showLoading();
                                        self.drop_work_pack = self.wor_pac_sel.value;
                                        self.drop_sub_proj = self.sub_pro_sel.value;
                                        self.drop_sub_pack = this.value;

                            var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack
                            var dateEntered = document.getElementById('select').value
                            dateEntered = dateEntered.replace(' to ','to');
                            var from = dateEntered.split('to')[0].replace(' ','');
                            var to = dateEntered.split('to')[1].replace(' ','');
                            var placeholder = ''
                            var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                                  + '&center=' + self.location + '&type=' + 'day'  + final_work;
                            $http({method:"GET", url:from_to_data}).success(function(result){
                                self.chart_render(result,self.project,self.location);
                            });
                                    });

                            }
                            else {
                                if ((result.result.fin.work_packet) && (result.result.fin.sub_packet)){
                                    $('#0').on('change', function(){
                                        self.showLoading();
                                        self.drop_work_pack = this.value;
                                        self.drop_sub_proj = 'undefined';
                                        self.drop_sub_pack = self.sub_pac_sel.value;
                                            if (self.day_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.day_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }

                                            if (self.day_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }


                            var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack
                            var dateEntered = document.getElementById('select').value
                            dateEntered = dateEntered.replace(' to ','to');
                            var from = dateEntered.split('to')[0].replace(' ','');
                            var to = dateEntered.split('to')[1].replace(' ','');
                            var placeholder = ''
                            var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                                  + '&center=' + self.location + '&type=' + 'day'  + final_work;
                            $http({method:"GET", url:from_to_data}).success(function(result){
                                self.chart_render(result,self.project,self.location);
                            });
                                    });
                                }
                                else{
                                    if (result.result.fin.work_packet){
                                        self.pack_day_type = result.result.days_type;
                                        $('#0').on('change', function(){
                                            self.showLoading();
                                            self.drop_work_pack = this.value;
                                            self.drop_sub_proj = 'undefined';
                                            self.drop_sub_pack = 'undefined';
                                            if (self.day_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.day_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }

                                            if (self.day_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }
                                            var is_exist = self.drop_work_pack.indexOf('&');
                                            if (is_exist > 0){
                                                self.drop_work_pack = self.drop_work_pack.replace(' & ',' and ')
                                            }
                            var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack;
                            var dateEntered = document.getElementById('select').value
                            dateEntered = dateEntered.replace(' to ','to');
                            var from = dateEntered.split('to')[0].replace(' ','');
                            var to = dateEntered.split('to')[1].replace(' ','');
                            var placeholder = ''
                            var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                                  + '&center=' + self.location + '&type=' + 'day'  + final_work;
                            $http({method:"GET", url:from_to_data}).success(function(result){
                                self.chart_render(result,self.project,self.location);
                            });
                                    })
                                }
                                }
                                if (result.result.fin.sub_packet) {
                                    $('#1').on('change', function(){
                                            if (self.day_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.day_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }

                                            if (self.day_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'day'){
                                                $('.day2').addClass('active btn-success');
                                                $('.day2').siblings().removeClass('active btn-success');
                                                $('.day').addClass('active btn-success');
                                                $('.day').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'week'){
                                                $('.week2').addClass('active btn-success');
                                                $('.week2').siblings().removeClass('active btn-success');
                                                $('.week').addClass('active btn-success');
                                                $('.week').siblings().removeClass('active btn-success');
                                            }
                                            if (self.sel_type === 'month'){
                                                $('.month2').addClass('active btn-success');
                                                $('.month2').siblings().removeClass('active btn-success');
                                                $('.month').addClass('active btn-success');
                                                $('.month').siblings().removeClass('active btn-success');
                                            }
                                        self.showLoading();
                                        self.drop_sub_pack = this.value;
                                        self.drop_sub_proj = 'undefined';
                                        self.drop_work_pack;
            var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.drop_work_pack
            var dateEntered = document.getElementById('select').value
            dateEntered = dateEntered.replace(' to ','to');
            var from = dateEntered.split('to')[0].replace(' ','');
            var to = dateEntered.split('to')[1].replace(' ','');
            var placeholder = ''
            var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                   + '&center=' + self.location + '&type=' + 'day'  + final_work;
            $http({method:"GET", url:from_to_data}).success(function(result){
                            self.chart_render(result,self.project,self.location);
            });

                                    });
                                }
                                else {
                                    self.drop_sub_pack = 'undefined';
                                    console.log('sub_packet_not_exist');
                                }
                            }
                        self.packet_count = result.result.productivity_data.length;
                            self.chart_render(result,self.project,self.location);
                        self.removeOptions = function (selectbox){
                            var i;
                            for(i = selectbox.options.length - 1 ; i >= 0 ; i--)
                                {
                                    selectbox.remove(i);
                                }
                            }*/
             var unWatch;

             this.$onInit = function () {
                unWatch = $scope.$watch(function(scope) {
                    return scope.options.state;
                },
                function(newVal){
                    if (newVal.state) {
                        $scope.radioModel = 'Day';
                        self.location = newVal.state.split(' - ')[0] + ' - ';
                        self.project = newVal.state.split(' - ')[1] + ' - ';
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
                        var url_to_call = 'api/project/?name=' + newVal.state;
                        $http({method:"GET", url:url_to_call}).success(function(result){
                            var pro_cen_nam = self.location + self.project.replace(' - ','');
                            self.useful_layout = [];
                            self.list_object = result.result.lay[0];
                if((result.result.role === 'customer') || (result.result.role === 'team_lead') || (result.result.role === 'center_manager') || (result.result.role === 'nextwealth_manager'))
                {
                    self.first = result.result.dates.from_date;
                    self.lastDate = self.first;
                    self.last = result.result.dates.to_date;
                    self.firstDate = self.last;
                    $('#select').val(self.first + ' to ' + self.last)

                    if ((result.result.role === 'customer') || (result.result.role === 'team_lead') || (result.result.role === 'nextwealth_manager') || (result.result.role === 'center_manager')){
                       self.layout_list = result.result.lay[1].layout;
                    }
                    else {
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
                    'self.chartOptions44':self.chartOptions44,
                    'self.chartOptions45':self.chartOptions45,
                    'self.chartOptions46':self.chartOptions46

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
                    self.project = pro_cen_nam.split('-')[1].replace(' ','') + ' - '
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

            /*self.dateType = function(key,all_data,name,button_clicked){
                self.day_type = key;
                var obj = {"self.chartOptions":self.chartOptions,"self.chartOptions9":self.chartOptions9,"self.chartOptions9_2":self.chartOptions9_2,"self.chartOptions10":self.chartOptions10,"self.chartOptions15":self.chartOptions15,"self.chartOptions16":self.chartOptions16,"self.chartOptions16_2":self.chartOptions16_2,"self.chartOptions17":self.chartOptions17,"self.chartOptions18":self.chartOptions18,"self.chartOptions19":self.chartOptions19,"self.chartOptions20":self.chartOptions20,'self.chartOptions21':self.chartOptions21,'self.chartOptions24':self.chartOptions24,'self.chartOptions25':self.chartOptions25,'self.chartOptions26':self.chartOptions26,'self.chartOptions38':self.chartOptions38,'self.chartOptions39':self.chartOptions39,'self.chartOptions40':self.chartOptions40,'self.chartOptions41':self.chartOptions41,'self.chartOptions42':self.chartOptions42}
                self.render_data = obj[all_data];
                self.high_data = [];
                self.button_clicked = button_clicked;
                self.packet_clicked = self.drop_work_pack;
                var is_exist = self.packet_clicked.indexOf('&');
                if (is_exist > 0){
                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                }
                var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.packet_clicked + '&is_clicked=' + self.button_clicked;
                var dateEntered = document.getElementById('select').value;
                dateEntered = dateEntered.replace(' to ','to');
                var from = dateEntered.split('to')[0].replace(' ','');
                var to = dateEntered.split('to')[1].replace(' ','');
                var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                        + '&center=' + self.location + '&type=' + self.day_type + final_work;
                console.log(from_to_data);
                $http({method:"GET", url:from_to_data}).success(function(result){
                            self.high_data_gener = [];
                            var final_data_gener = result.result;
                            self.high_data_gener.push(final_data_gener);
                if (name === 'chartOptions'){

                  angular.extend(self.render_data, {

                      xAxis: {
                         categories: self.high_data_gener[0].data.date,
                         title: {
                          text: '',
                         }
                       },
                       plotOptions: {
                        series : {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            point: {
                                events:{
                                click : function() {

                                if ($("body").hasClass("add_annotation")) {

                                    return;
                                }

                                var chart_name = 'productivity_chart';
                                var is_drill = self.list_object[chart_name].is_drilldown;
                                if (is_drill){
                                var addition = '&project=' +self.project + '&center=' +self.location;
                                var productivity_graph ='/api/chart_data/?'
                                self.packet_clicked = this.series.name;
                                var is_exist = self.packet_clicked.indexOf('&');
                                if (is_exist > 0){
                                self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                                }
                                $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + this.category +
                                '&type=' + 'Production Trends' + addition).success(
                                function(data, status)
                                        {
                                            $('#myModal').modal('show');
                                            self.names = data.result.data;
                                            var proj = data.result.project;
                                            var pro_drill = data.result.table_headers;
                                            var chart_type = data.result.type;
                                            self.fields_list_drilldown = pro_drill;
                                            self.chart_type = data.result.type;
                                            console.log(self.names);
                                        }).error(function(error){ console.log("error")});
                                        }
                                },contextmenu: function(){
                                
                                return new Annotation("productivity_chart<##>Week", $(event.currentTarget),this.series.chart, this);

                                    }
                            }
                        },
                        bar: {
                         dataLabels: {
                         enabled: true
                         }
                        }
                       }
                       },
                       series: self.high_data_gener[0].productivity_data,

                       onComplete: function(chart){

                         var series = null;

                         var chart_data = chart.series;

                         for(var i in chart_data){

                           series = chart_data[i];

                           (function(series){

                             $http({method:"GET", url:"/api/annotations/?series_name="+series.name+'&type=week'+'&chart_name='+'productivity_chart'}).success(function(annotations){

                               annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });

                               $.each(annotations, function(j, annotation){

                                 var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                 point = point[0];

                                 if(annotation.epoch){
                                   var a = new Annotation("productivity_chart", $(self.chartOptions.chart.renderTo.innerHTML),
                                        chart, point, annotation);

                                   console.log(a);
                                   }
                               })

                             })
                           }(series));
                         }
                       }
                    });
                  }

             if (name === 'chartOptions38') {
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'Production_avg_perday';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Production Trends' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }

                        }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].production_avg_details
             });
             }

             if (name === 'chartOptions39') {
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].upload_target_data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'target_upload_graph';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Upload Accuracy' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }

                        }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].upload_target_data.data
             });
             }

            if (name === 'chartOptions40') {
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'pre_scan_exception_chart';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Pre Scan Exception Chart' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }

                        }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].pre_scan_exception_data
             });
             }

             if (name === 'chartOptions41') {
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'overall_exception_chart';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Overall Exception' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }

                        }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].overall_exception_details
             });
             }

             if (name === 'chartOptions42') {
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'nw_exception_chart';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'NW Exception' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }

                        }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].nw_exception_details
             });
             }

             if (name === 'chartOptions38') {
             angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'Production_avg_perday';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Production Trends' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }

                        }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].production_avg_details
             });
             } 

             if (name === 'chartOptions10'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        click: function() {
                        var chart_name = 'productivity_bar_graph';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        //console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = this.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + this.category +
                        '&type=' + 'Production Chart' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    //var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    //self.fields_list_drilldown = pro_drill[chart_type];
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].productivity_data
                     });
             }

           if (name === 'chartOptions16'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'total_fte';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'FTE Utilized _Workpacket Wise' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].fte_calc_data.work_packet_fte
                     });
             } 


            if (name === 'chartOptions25'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'operational_utilization';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Operational Utilization' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].utilization_operational_details
                     });

}


          if (name === 'chartOptions26'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'monthly_volume widget';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Monthly Volume' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].monthly_volume_graph_details
                     });
             } 


           if (name === 'chartOptions24'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'fte_utilization';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'FTE Utilization' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].utilization_fte_details
                     });
             } 


            if (name === 'chartOptions16_2'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'sum_total_fte';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Total FTE Utilized' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].fte_calc_data.total_fte
                     });
             }

            if (name === 'chartOptions20'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'internal_pareto_ analysis';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'Internal Pareto Analysis' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].internal_pareto_graph_data
                     });
             }

           if (name === 'chartOptions21'){
                            angular.extend(self.render_data, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                        select: function(e) {
                        var chart_name = 'external_pareto_ analysis';
                        var is_drill = self.list_object[chart_name].is_drilldown;
                        if (is_drill){
                        var addition = '&project=' +self.project + '&center=' +self.location;
                        console.log(e.target.series.name);
                        var productivity_graph ='/api/chart_data/?'
                        self.packet_clicked = e.target.series.name;
                        var is_exist = self.packet_clicked.indexOf('&');
                        if (is_exist > 0){
                        self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                        }
                        $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                        '&type=' + 'External Pareto Analysis' + addition).success(
                        function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               }
               },
               series: self.high_data_gener[0].external_pareto_graph_data
                     });
             } 


            if (name === 'chartOptions15'){
                angular.extend(self.render_data,{
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {   
                        events:{
                            select: function(e) {
                            var chart_name = 'utilisation_wrt_work_packet';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + self.project + '&center=' + self.location;
                            console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                                                 self.packet_clicked = e.target.series.name;
                                                 var is_exist = self.packet_clicked.indexOf('&');
                                                 if (is_exist > 0){
                                                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                                                 }
                            $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                             '&type=' + 'Utilisation Trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                   }).error(function(error){ console.log("error")});
                                }
               }
                    }
                },   
                bar: {
                 dataLabels: {
                 enabled: true 
                 }
                }
               }
               },   
               series: self.high_data_gener[0].original_utilization_graph
                     });  
             }
 



             if (name === 'chartOptions9'){
                angular.extend(self.render_data,{
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                            click: function() {
                            var chart_name = 'internal_accuracy_timeline';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + self.project + '&center=' + self.location;
                            //console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                                                 self.packet_clicked = this.series.name;
                                                 var is_exist = self.packet_clicked.indexOf('&');
                                                 if (is_exist > 0){
                                                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                                                 }
                            $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + this.category +
                             '&type=' + 'Internal Accuracy Trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    //var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    //self.fields_list_drilldown = pro_drill[chart_type];
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].internal_time_line
                            });
             }
        
            if (name === 'chartOptions19'){
                angular.extend(self.render_data,{
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },   
                            plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                            select: function(e) {
                            var chart_name = 'productivity_trends';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + self.project + '&center=' + self.location;
                            console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                                                 self.packet_clicked = e.target.series.name;
                                                 var is_exist = self.packet_clicked.indexOf('&');
                                                 if (is_exist > 0){
                                                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                                                 }
                            $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + e.target.category +
                             '&type=' + 'Productivity trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },   
                bar: {
                 dataLabels: {
                 enabled: true 
                 }
                }
               },   
                            series: self.high_data_gener[0].original_productivity_graph
                            });  
             }



            if (name === 'chartOptions9_2'){
                angular.extend(self.render_data,{
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                            click: function() {
                            var chart_name = 'external_accuracy_timeline';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + self.project + '&center=' + self.location;
                            //console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                                                 self.packet_clicked = this.series.name;
                                                 var is_exist = self.packet_clicked.indexOf('&');
                                                 if (is_exist > 0){
                                                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                                                 }
                            $http.get( productivity_graph+ 'packet=' + self.packet_clicked + '&date=' + this.category +
                             '&type=' + 'External Accuracy Trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    //var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    //self.fields_list_drilldown = pro_drill[chart_type];
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].external_time_line
                            }); 
            }
            if (name === 'chartOptions17'){
                            angular.extend(self.render_data, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                            },   
                            series: self.high_data_gener[0].volume_graphs.bar_data
                            });  
                            angular.extend(self.render_data.plotOptions.series.point.events,{
                            select: function(e) {
                            var addition = '&project=' + pro + '&center=' + loc; 
                            console.log(e.target.name);
                            var productivity_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            $http.get( productivity_bar_graph + 'packet=' + e.target.series.name + '&date=' + e.target.category
                             + '&type=' + 'Production Chart'+addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});

                            }
                            });

            }
            if (name === 'chartOptions18'){
                                            angular.extend(self.render_data, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {

                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].volume_graphs.line_data
             });
 
            }
                         });
            }*/

            self.active_filters = function(type,button_clicked){
                self.button_clicked = button_clicked;
                var some = '' 
                if (type == 'day') { some = 'Day';}
                if (type == 'week') { some = 'Week';}
                if (type == 'month') { some = 'Month';}
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
                self.packet_clicked = self.drop_work_pack;
                var is_exist = self.packet_clicked.indexOf('&');
                if (is_exist > 0){
                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                }
                var dateEntered = document.getElementById('select').value
                dateEntered = dateEntered.replace(' to ','to');
                self.lastDate = dateEntered.split('to')[0].replace(' ','');
                self.firstDate  = dateEntered.split('to')[1].replace(' ','');
                var placeholder = '' 
                var final_work =  '&sub_project=' + self.drop_sub_proj + '&sub_packet=' + self.drop_sub_pack + '&work_packet=' + self.packet_clicked + '&is_clicked=' + self.button_clicked;
                var from_to_data = from_to +'from=' + self.lastDate + '&to=' + self.firstDate + '&project=' + self.project + '&center=' + self.location + '&type=' + type + final_work; 
                $http({method:"GET", url:from_to_data}).success(function(result){
                    self.chart_render(result,self.project,self.location);
                });  

            } 

            self.chart_render = function(result,pro,loc){

                            self.high_data_gener = [];
                            var final_data_gener = result.result;
                            self.high_data_gener.push(final_data_gener);
                            self.top_employee_details =  result.result.top_five_employee_details;
                            self.top_five = result.result.only_top_five;
                            self.volume_graphs = result.result.volumes_graphs_details;
                           /* self.drop_list = [];
                            self.drop_list =  result.result.drop_value;

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

                        for (var sub_pro in self.drop_list) {
                            self.sub_pro_sel.options[self.sub_pro_sel.options.length] = new Option(sub_pro, sub_pro);
                        }
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
                                //self.wor_pac_sel.selectedIndex=1;
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
                            }*/

            
                            angular.extend(self.chartOptions, {

                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },

                                plotOptions: {

                                     series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             click: function() {

                                             if ($("body").hasClass("add_annotation")) {

                                                return;
                                             }

                                             var chart_name = 'productivity_chart';

                                             var is_drill = self.list_object[chart_name].is_drilldown;

                                             if (is_drill){

                                               var addition = '&project=' +pro + '&center=' +loc;

                                               //console.log(e.target.series.name);

                                               var productivity_graph ='/api/chart_data/?';

                                               var packet_clicked = this.series.name;

                                               var is_exist = packet_clicked.indexOf('&');

                                               if (is_exist > 0){

                                                 packet_clicked = packet_clicked.replace(' & ',' and ')
                                               }

                                               $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + this.category +
                                                    '&type=' + 'Production Trends' + addition).success(

                                                    function(data, status){

                                                        $('#myModal').modal('show');

                                                        self.names = data.result.data;

                                                        var proj = data.result.project;

                                                        var pro_drill = data.result.table_headers;

                                                        var chart_type = data.result.type;

                                                        var pro_value = '';
                                                        var aud_value = '';
                                                        self.error_count = '';
                                                        self.audited_count = '';
                                                        if (aud_value === undefined) {
                                                          self.audited_count = pro_value;
                                                        }

                                                        self.fields_list_drilldown = pro_drill;

                                                        self.chart_type = data.result.type;

                                                        console.log(self.names);

                                                    }).error(function(error){ console.log("error")});
                                         }
                        }, contextmenu: function () {

                          return new Annotation("productivity_chart", $(event.currentTarget), this.series.chart, this);
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].productivity_data,
               onComplete: function(chart){

                 var series = null;

                 var chart_data = chart.series;

                 for(var i in chart_data){

                   series = chart_data[i];

                   (function(series){

                     $http({method:"GET", url:"/api/annotations/?series_name="+series.name+"&chart_name="+'productivity_chart'}).success(function(annotations){

                       annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });

                       $.each(annotations, function(j, annotation){

                         var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                         point = point[0];

                         if(annotation.epoch){
                           var a = new Annotation("productivity_chart", $(self.chartOptions.chart.renderTo),
                                chart, point, annotation);

                           console.log(a);
                           }
                       })

                     })
                   }(series));
                 }
               }
             });

                          angular.extend(self.chartOptions38, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                     series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'Production_avg_perday';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].production_avg_details
             });


                           angular.extend(self.chartOptions39, {
                                xAxis: {
                                    categories: self.high_data_gener[0].upload_target_data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                     series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'target_upload_graph';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Upload Accuracy' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].upload_target_data.data,
             });

                           angular.extend(self.chartOptions40, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                     series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'pre_scan_exception_chart';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Pre Scan Exception Chart' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].pre_scan_exception_data
             });

                           angular.extend(self.chartOptions41, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                     series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'overall_exception_chart';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Overall Exception' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].overall_exception_details
             });

                           angular.extend(self.chartOptions42, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                     series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'nw_exception_chart';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'NW Exception' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].nw_exception_details
             }); 

                            angular.extend(self.chartOptions9_2.yAxis,{
                                min:result.result.min_external_time_line,
                                max:result.result.max_external_time_line
                            });
                            angular.extend(self.chartOptions9_2, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },



plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                            click: function() {
                            var chart_name = 'external_accuracy_timeline';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            //console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                                                 var packet_clicked = this.series.name;
                                                 var is_exist = packet_clicked.indexOf('&');
                                                 if (is_exist > 0){
                                                    packet_clicked = packet_clicked.replace(' & ',' and ')
                                                 }

                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + this.category +
                             '&type=' + 'External Accuracy Trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    var pro_value = data.result.Productivity_value;
                                    var aud_value = data.result.audited_value;
                                    self.error_count = data.result.Error_count;
                                    self.audited_count = aud_value;
                                    if (aud_value === undefined) {
                                      self.audited_count = pro_value;
                                    }
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },

                            series: self.high_data_gener[0].external_time_line
                            });
                            angular.extend(self.chartOptions9.yAxis,{
                                min:result.result.min_internal_time_line,
                                max:result.result.max_internal_time_line
                            });
                            angular.extend(self.chartOptions9, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },

                plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    point: {
                        events:{
                            click: function() {
                                             if ($("body").hasClass("add_annotation")) {

                                                return;
                                             }

                            var chart_name = 'internal_accuracy_timeline';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            //console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                                                 var packet_clicked = this.series.name;
                                                 var is_exist = packet_clicked.indexOf('&');
                                                 if (is_exist > 0){
                                                    packet_clicked = packet_clicked.replace(' & ',' and ')
                                                 }

                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + this.category +
                             '&type=' + 'Internal Accuracy Trends' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    //var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    var pro_value = data.result.Productivity_value;
                                    var aud_value = data.result.audited_value;
                                    self.error_count = data.result.Error_count;
                                    self.audited_count = aud_value;
                                    if (aud_value === undefined) {
                                      self.audited_count = pro_value;
                                    } 
                                    self.fields_list_drilldown = pro_drill;
                                    //self.fields_list_drilldown = pro_drill[chart_type];
                                    //self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }, contextmenu: function () {

                          return new Annotation("internal_accuracy_timeline", $(event.currentTarget), this.series.chart, this);
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].internal_time_line,
               onComplete: function(chart){

                 var series = null;

                 var chart_data = chart.series;

                 for(var i in chart_data){

                   series = chart_data[i];

                   (function(series){

                     $http({method:"GET", url:"/api/annotations/?series_name="+series.name+"&chart_name="+'internal_accuracy_timeline'}).success(function(annotations){

                       annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });

                       $.each(annotations, function(j, annotation){

                         var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                         point = point[0];

                         if(annotation.epoch){
                           var a = new Annotation("internal_accuracy_timeline", $(self.chartOptions9.chart.renderTo),
                                chart, point, annotation);

                           console.log(a);
                           }
                       })

                     })
                   }(series));
                 }
               }

                            });

                            angular.extend(self.chartOptions19.yAxis,{
                                min:result.result.min_original_productivity_graph,
                                max:result.result.max_original_productivity_graph
                            });

                            angular.extend(self.chartOptions19, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].original_productivity_graph
                            });
                            angular.extend(self.chartOptions20, {

                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].internal_pareto_graph_data
                            });

                            angular.extend(self.chartOptions21, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].external_pareto_graph_data
                            });



                           angular.extend(self.chartOptions27, {

                            xAxis: {
                                categories: self.high_data_gener[0].Pareto_data.emp_names,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].Pareto_data.agent_pareto_data
                            });


                            angular.extend(self.chartOptions28, {

                            xAxis: {
                                categories: self.high_data_gener[0].External_Pareto_data.emp_names,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].External_Pareto_data.agent_pareto_data
                            });


                            angular.extend(self.chartOptions29, {

                            xAxis: {
                                categories: self.high_data_gener[0].Internal_Error_Category.category_name,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].Internal_Error_Category.category_pareto
                            });

                            angular.extend(self.chartOptions31.yAxis,{
                                min:result.result.min_tat_details,
                                max:result.result.max_tat_details
                            });                              

                            /*angular.extend(self.chartOptions31, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].tat_details
                            }); */




                            angular.extend(self.chartOptions30, {

                            xAxis: {
                                categories: self.high_data_gener[0].External_Error_Category.category_name,
                                title: {
                                    text: '',
                                }
                            },
plotOptions: {
                series : {
                    allowPointSelect: true,
                    cursor: 'pointer'
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
                            series: self.high_data_gener[0].External_Error_Category.category_pareto
                            });
                                                                                    

                            angular.extend(self.chartOptions10, {

                            plotOptions:{

                                series:{
                                    allowPointSelect: true,
                                    cursor: 'pointer',
                                point: {
                                    events:{
                                        click: function() {

                                if ($("body").hasClass("add_annotation")) {

                                    return;
                                }

                              var chart_name = 'productivity_bar_graph';

                              var is_drill = self.list_object[chart_name].is_drilldown;

                                if (is_drill){

                                  var addition = '&project=' + pro + '&center=' + loc; 

                                  var productivity_bar_graph ='/api/chart_data/?';

                                  var packet_clicked = this.series.name;

                                  var is_exist = packet_clicked.indexOf('&');

                                  if (is_exist > 0){

                                    packet_clicked = packet_clicked.replace(' & ',' and ')

                                  }

                                  var dates_list = self.get_date();

                                  $http.get( productivity_bar_graph + 'packet=' + packet_clicked + '&date=' + this.category
                                        + '&type=' + 'Production Chart'+addition).success(

                                        function(data, status){

                                            $('#myModal').modal('show');

                                            self.names = data.result.data;

                                            var proj = data.result.project;

                                            var pro_drill = data.result.table_headers;

                                            var chart_type = data.result.type;

                                            self.fields_list_drilldown = pro_drill;

                                            self.chart_type = data.result.type;

                                            console.log(self.names);

                                       }).error(function(error){ console.log("error")});
                                }
                                }, contextmenu: function () {

                                    return new Annotation("productivity_bar_graph", $(event), this.series.chart, this);
                                }

                                    }
                                }
                                }
                            },

                            xAxis: {

                                categories: self.high_data_gener[0].data.date
                            },

                            series: self.high_data_gener[0].productivity_data,

                            onComplete: function(chart) {

                                 var series = null;

                                 var chart_data = chart.series;

                                 for(var i in chart_data){

                                   series = chart_data[i];

                                   (function(series){

                                     $http({method:"GET", url:"/api/annotations/?series_name="+series.name+"&chart_name="+'productivity_chart'}).success(function(annotations){

                                       annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });

                                       $.each(annotations, function(j, annotation){

                                         var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                                         point = point[0];

                                         if(annotation.epoch){
                                           var a = new Annotation("productivity_bar_graph", $(self.chartOptions10.chart.renderTo),
                                                chart, point, annotation);

                                           console.log(a);
                                           }
                                       })

                                     })
                                   }(series));
                                 }
                               }
                             });


                            angular.extend(self.chartOptions17, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                            },
                            series: self.high_data_gener[0].volume_graphs.bar_data
                            });
                            angular.extend(self.chartOptions17.plotOptions.series.point.events,{
                            select: function(e) {
                            var chart_name = 'volume_bar_graph';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var productivity_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            $http.get( productivity_bar_graph + 'packet=' + e.target.series.name + '&date=' + e.target.category
                             + '&type=' + 'Production Chart'+addition).success(
                            function(data,  status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });
                            angular.extend(self.chartOptions18, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'volume_productivity_graph';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){ 
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].volume_graphs.line_data
             });

                          angular.extend(self.chartOptions31, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             click: function() {
                                                             if ($("body").hasClass("add_annotation")) {

                                                return;
                                             }
                                             var chart_name = 'Tat Graph';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             //console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = this.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + this.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    //var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = data.result.type;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }, contextmenu: function () {
                            return new Annotation('Tat Graph',$(event.currentTarget), this.series.chart, this);
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].tat_graph_details,
               onComplete: function(chart){

                 var series = null;

                 var chart_data = chart.series;

                 for(var i in chart_data){

                   series = chart_data[i];

                   (function(series){

                     $http({method:"GET", url:"/api/annotations/?series_name="+series.name+"&chart_name="+'Tat Graph'}).success(function(annotations){

                       annotations = _.sortBy(annotations.result, function(annotation){ return annotation.epoch });

                       $.each(annotations, function(j, annotation){
              var point = _.filter(series.points, function(point){ return point.category == annotation.epoch});

                         point = point[0];

                         if(annotation.epoch){
                           var a = new Annotation("Tat Graph", $(self.chartOptions9.chart.renderTo),
                                chart, point, annotation);

                           console.log(a);
                           }
                       })

                     })
                   }(series));
                 }
               }
             });    

                            angular.extend(self.chartOptions26, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'monthly_volume widget';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Monthly Volume' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].monthly_volume_graph_details
             });

                            angular.extend(self.chartOptions5,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    cursor: 'pointer',
                                    data: self.high_data_gener[0].internal_errors_types
                                }]
                            });
                            angular.extend(self.chartOptions5.plotOptions.pie.point.events,{
                            select: function(e) {
                            var chart_name = 'internal_error_accuracy_pie';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            //var dates_list = [self.start,self.end];
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'Internal_Bar_Pie' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    //self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });

                            angular.extend(self.chartOptions45,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    cursor: 'pointer',
                                    data: self.high_data_gener[0].internal_sub_error_types
                                }]
                            });

                            angular.extend(self.chartOptions23,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    cursor: 'pointer',
                                    data: self.high_data_gener[0].internal_errors_types
                                }]
                            });
                            angular.extend(self.chartOptions23.plotOptions.pie.point.events,{
                            select: function(e) {
                            var chart_name = 'tat';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            //var dates_list = [self.start,self.end];
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'TAT' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    //self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });

                            angular.extend(self.chartOptions45.plotOptions.pie.point.events,{
                            select: function(e) {
                            var chart_name = 'internal_sub_error_category_wise';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'Internal Error Sub Category Wise' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });

                            angular.extend(self.chartOptions46,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    cursor: 'pointer',
                                    data: self.high_data_gener[0].external_sub_error_types
                                }]
                            });

                            angular.extend(self.chartOptions46.plotOptions.pie.point.events,{
                            select: function(e) {
                            var chart_name = 'external_sub_error_category_wise';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'External Error Sub Category Wise' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });

                            angular.extend(self.chartOptions5_2,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    cursor: 'pointer',
                                    data: self.high_data_gener[0].external_errors_types
                                }]
                            });
                            angular.extend(self.chartOptions5_2.plotOptions.pie.point.events,{
                            select: function(e) {
                            var chart_name = 'external_error_accuracy_pie';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var external_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            //var dates_list = [self.start,self.end];
                            $http.get( external_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'External_Bar_Pie'+ addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = drilldown_config[proj];
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill[chart_type];
                                    //self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });
                            angular.extend(self.chartOptions4.yAxis.title,{
                                text: ''
                            });
                            angular.extend(self.chartOptions4.plotOptions.series.point.events,{
                            click: function() {
                            var chart_name = 'internal_error_accuracy';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            //var dates_list = [self.start,self.end];
                            var packet_clicked = this.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'Internal Accuracy'+addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    //var pro_drill = drilldown_config[proj];
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    var pro_value = data.result.Productivity_value;
                                    var aud_value = data.result.audited_value;
                                    self.error_count = data.result.Error_count;
                                    self.audited_count = aud_value;
                                    if (aud_value === undefined) {
                                      self.audited_count = pro_value;
                                    }
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });
                            angular.extend(self.chartOptions4,{
              series: [{
                 name: 'accuracy',
                 cursor: 'pointer',
                 colorByPoint: true,
                    data: self.high_data_gener[0].internal_accuracy_graph
             }]
             });



                            angular.extend(self.chartOptions43.yAxis.title,{
                                text: ''
                            });
                            angular.extend(self.chartOptions43.plotOptions.series.point.events,{
                            select: function(e) {
                            var chart_name = 'internal_field_accuracy_graph';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'Internal Field Accuracy'+addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });
                            angular.extend(self.chartOptions43,{
                                series: [{
                                    name: 'accuracy',
                                    cursor: 'pointer',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].internal_field_accuracy_graph
                                }]
                            });

                           angular.extend(self.chartOptions4.yAxis.title,{
                                text: ''
                            });
                            angular.extend(self.chartOptions44.plotOptions.series.point.events,{
                            select: function(e) {
                            var chart_name = 'external_field_accuracy_graph';
                            var is_drill = self.list_object[chart_name].is_drilldown;
                            if (is_drill){
                            var addition = '&project=' + pro + '&center=' + loc;
                            console.log(e.target.name);
                            var internal_bar_graph ='/api/chart_data/?';
                            var dates_list = self.get_date();
                            var packet_clicked = e.target.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            $http.get( internal_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'External Field Accuracy'+addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                            }
                            });
                            angular.extend(self.chartOptions44,{
                                series: [{
                                    name: 'accuracy',
                                    cursor: 'pointer',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].external_field_accuracy_graph
                                }]
                            });

                            angular.extend(self.chartOptions44.yAxis,{
                                //min:result.result.ext_min_value,
                                //max:result.result.ext_max_value
                                min:result.result.exter_min_value,
                                max:result.result.exter_max_value
                            });

                            angular.extend(self.chartOptions43.yAxis,{
                                //min:result.result.ext_min_value,
                                //max:result.result.ext_max_value
                                min:result.result.inter_min_value,
                                max:result.result.inter_max_value
                            });

                            angular.extend(self.chartOptions6.yAxis.title,{
                                text: ''
                            });
                            angular.extend(self.chartOptions4.yAxis,{
                                min:result.result.int_min_value,
                                max:result.result.int_max_value
                            });
                            angular.extend(self.chartOptions6.plotOptions.series.point.events,{
                click: function() {
                var chart_name = 'external_error_accuracy';
                var is_drill = self.list_object[chart_name].is_drilldown;
                if (is_drill){
                var addition = '&project=' + pro + '&center=' + loc;
                        
                            var external_bar_graph ='/api/chart_data/?';
                            var packet_clicked = this.name;
                            var is_exist = packet_clicked.indexOf('&');
                            if (is_exist > 0){
                                packet_clicked = packet_clicked.replace(' & ',' and ')
                            }
                            var dates_list = self.get_date();
                            //var dates_list = [self.start,self.end];
                            $http.get( external_bar_graph + 'packet=' + packet_clicked + '&from=' + dates_list[0] + '&to=' + dates_list[1]
                             + '&type=' + 'External Accuracy' + addition).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    var proj = data.result.project;
                                    //var pro_drill = drilldown_config[proj];
                                    var pro_drill = data.result.table_headers;
                                    var chart_type = data.result.type;
                                    var pro_value = data.result.Productivity_value;
                                    var aud_value = data.result.audited_value;
                                    self.error_count = data.result.Error_count;
                                    self.audited_count = aud_value;
                                    if (aud_value === undefined) {
                                      self.audited_count = pro_value;
                                    }
                                    self.fields_list_drilldown = pro_drill;
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
              });
                            angular.extend(self.chartOptions6,{
              series: [{
                 name: 'accuracy',
                 colorByPoint: true,
                 cursor: 'pointer',
                    data: self.high_data_gener[0].external_accuracy_graph
             }]
             });
                            angular.extend(self.chartOptions6.yAxis,{
                                min:result.result.ext_min_value,
                                max:result.result.ext_max_value
                            });

                            angular.extend(self.chartOptions15.yAxis,{
                                min:result.result.min_original_utilization_graph,
                                max:result.result.max_original_utilization_graph
                            });

                            angular.extend(self.chartOptions15, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                    },
                                    bar: {
                                        dataLabels: {
                                            enabled: true
                                        }
                                    }
                                },
                                series: self.high_data_gener[0].original_utilization_graph
                                    });
                            

                           /* angular.extend(self.chartOptions24.yAxis,{
                                min:result.result.min_utilization_fte_details,
                                max:result.result.max_utilization_fte_details
                            });*/


                            angular.extend(self.chartOptions24, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'fte_utilization';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].utilization_fte_details
             });




                            /*angular.extend(self.chartOptions25.yAxis,{
                                min:result.result.min_utilization_operational_details,
                                max:result.result.max_utilization_operational_details
                            });*/


                            angular.extend(self.chartOptions25, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {
                                             var chart_name = 'operational_utilization';
                                             var is_drill = self.list_object[chart_name].is_drilldown;
                                             if (is_drill){
                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});
                                }
                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].utilization_operational_details
             });


                            angular.extend(self.chartOptions15_2, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                    },
                                    bar: {
                                        dataLabels: {
                                            enabled: true
                                        }
                                    }
                                },
                                series: self.high_data_gener[0].utilization_work_packet_details
                            });
                            angular.extend(self.chartOptions16, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                    },
                                    bar: {
                                        dataLabels: {
                                            enabled: true
                                        }
                                    }
                                },
                                series: self.high_data_gener[0].fte_calc_data.work_packet_fte
                            });
                            angular.extend(self.chartOptions16_2, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                    },
                                    bar: {
                                        dataLabels: {
                                            enabled: true
                                        }
                                    }
                                },
                                series: self.high_data_gener[0].fte_calc_data.total_fte
                            });

            }

            self.static_widget_render = function(result,pro,loc) {
                self.high_data_gener = [];
                var final_data_gener = result.result;
                self.high_data_gener.push(final_data_gener);
                angular.extend(self.chartOptions32, {
                    xAxis: {
                        categories: self.high_data_gener[0].month_productivity_data.date,
                        title: {
                            text: '',
                        }
                    },
                    plotOptions: {
                        series : {
                            allowPointSelect: true,
                            cursor: 'pointer'
                        },
                        bar: {
                            dataLabels: {
                            enabled: true
                            }
                        }
                    },
                    series: self.high_data_gener[0].month_productivity_data.data,
                });

                angular.extend(self.chartOptions33, {
                    xAxis: {
                        categories: self.high_data_gener[0].week_productivity_data.date,
                        title: {
                            text: '',
                        }
                    },
                    plotOptions: {
                        series : {
                            allowPointSelect: true,
                            cursor: 'pointer'
                        },
                        bar: {
                            dataLabels: {
                            enabled: true
                            }
                        }
                    },
                    series: self.high_data_gener[0].week_productivity_data.data,
                });

                angular.extend(self.chartOptions35, {
                    xAxis: {
                        categories: self.high_data_gener[0].data.date,
                    },   
                    series: self.high_data_gener[0].data.data
                    });  
                angular.extend(self.chartOptions35.plotOptions.series.point.events,{
                    select: function(e) {
                    var chart_name = 'Static_Daily_Production_Bar';
                    var is_drill = self.list_object[chart_name].is_drilldown;
                    if (is_drill){
                    var addition = '&project=' + pro + '&center=' + loc; 
                    console.log(e.target.name);
                    var productivity_bar_graph ='/api/chart_data/?';
                    var dates_list = self.get_date();
                    $http.get( productivity_bar_graph + 'packet=' + e.target.series.name + '&date=' + e.target.category
                     + '&type=' + 'Production Chart'+addition).success(
                    function(data,  status)
                        {
                            $('#myModal').modal('show');
                            self.names = data.result.data;
                            self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                            self.chart_type = data.result.type;
                            console.log(self.names);
                        }).error(function(error){ console.log("error")});
                        }
                    }
                });

                angular.extend(self.chartOptions36, {
                    xAxis: {
                        categories: self.high_data_gener[0].week_productivity_data.date,
                    },   
                    series: self.high_data_gener[0].week_productivity_data.data
                });  
                angular.extend(self.chartOptions36.plotOptions.series.point.events,{
                    select: function(e) {
                    var chart_name = 'Static_Weekly_Production_Bar';
                    var is_drill = self.list_object[chart_name].is_drilldown;
                    if (is_drill){
                    var addition = '&project=' + pro + '&center=' + loc;
                    console.log(e.target.name);
                    var productivity_bar_graph ='/api/chart_data/?';
                    var dates_list = self.get_date();
                    $http.get( productivity_bar_graph + 'packet=' + e.target.series.name + '&date=' + e.target.category
                     + '&type=' + 'Production Chart'+addition).success(
                    function(data,  status)
                        {
                            $('#myModal').modal('show');
                            self.names = data.result.data;
                            self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                            self.chart_type = data.result.type;
                            console.log(self.names);
                        }).error(function(error){ console.log("error")});
                        }
                    }
                 });

                angular.extend(self.chartOptions37, {
                    xAxis: {
                        categories: self.high_data_gener[0].month_productivity_data.date,
                    },
                    series: self.high_data_gener[0].month_productivity_data.data
                    });
                angular.extend(self.chartOptions37.plotOptions.series.point.events,{
                    select: function(e) {
                    var chart_name = 'Static_Monthly_Production_Bar';
                    var is_drill = self.list_object[chart_name].is_drilldown;
                    if (is_drill){
                    var addition = '&project=' + pro + '&center=' + loc;
                    console.log(e.target.name);
                    var productivity_bar_graph ='/api/chart_data/?';
                    var dates_list = self.get_date();
                    $http.get( productivity_bar_graph + 'packet=' + e.target.series.name + '&date=' + e.target.category
                     + '&type=' + 'Production Chart'+addition).success(
                    function(data,  status)
                        {
                            $('#myModal').modal('show');
                            self.names = data.result.data;
                            self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                            self.chart_type = data.result.type;
                            console.log(self.names);
                        }).error(function(error){ console.log("error")});
                        }
                    }
                });      
        
                angular.extend(self.chartOptions34, {
                    xAxis: {
                        categories: self.high_data_gener[0].data.date,
                        title: {
                            text: '',
                        }
                    },
                    plotOptions: {
                        series : {
                            allowPointSelect: true,
                            cursor: 'pointer'
                        },
                        bar: {
                            dataLabels: {
                            enabled: true
                            }
                        }
                    },
                    series: self.high_data_gener[0].data.data,
                });
            }               

            self.get_date = function(){
                var dateEntered = document.getElementById('select').value;
                dateEntered = dateEntered.replace(' to ','to');
                var from = dateEntered.split('to')[0].replace(' ','');
                var to = dateEntered.split('to')[1].replace(' ','');
                return [from,to];
            };

            self.click = function(start,end){
                self.start = start.format('YYYY-MM-DD');
                self.end = end.format('YYYY-MM-DD');
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
                        $("#0").append(new Option("All"));
                        $("#1").append(new Option("All"));
                        $("#2").append(new Option("All"));

                //var dates_list = self.get_date();
                var final_packet_count = project_dropdown_count + '&project=' + self.project + '&center=' + self.location;
                var dropdown_selection_data = $http({method:"GET", url:final_packet_count}).success(function(result){
                        self.final_data_count =result.result;
                        var dropdown_sub_project = result.result.sub_project;
                        var dropdown_work_packet = result.result.work_packet;
                        var dropdown_sub_packet = result.result.sub_packet;

                var dates_list = [self.start,self.end];
                //var wor_pac = document.getElementById("0");
                var sub_pro = document.getElementById("0");
                //var sub_pac = document.getElementById("1");
                var wor_pac = document.getElementById("1"); 
                var sub_pac = document.getElementById("2");
                if (( dropdown_sub_project === 0) && (dropdown_work_packet  === 1) && (dropdown_sub_packet === 0)){ 
                    self.sub_pro_sel_two = 'undefined';
                    self.sub_pac_sel_two = 'undefined';
                    self.wor_pac_sel_two = sub_pro.value;
                }
                else if (( dropdown_sub_project == 0) && (dropdown_work_packet  == 1) && (dropdown_sub_packet == 1)){ 
                    self.sub_pro_sel_two = 'undefined'; 
                    self.sub_pac_sel_two = wor_pac.value;
                    self.wor_pac_sel_two = sub_pro.value;
                }    
                else if (( dropdown_sub_project == 1) && (dropdown_work_packet  == 1) && (dropdown_sub_packet == 1)){ 
                    self.sub_pro_sel_two = sub_pro.value; 
                    self.sub_pac_sel_two = sub_pac.value;
                    self.wor_pac_sel_two = wor_pac.value;
                }

                //self.wor_pac_sel_two = document.getElementById("0").value;
                //self.sub_pac_sel_two = document.getElementById("1").value;
                //self.sub_pro_sel_two = 'undefined';
                self.packet_clicked = self.wor_pac_sel_two;
                var is_exist = self.packet_clicked.indexOf('&');
                if (is_exist > 0){
                    self.packet_clicked = self.packet_clicked.replace(' & ',' and ')
                }
                var final_work =  '&sub_project=' + self.sub_pro_sel_two + '&sub_packet=' + self.sub_pac_sel_two + '&work_packet=' + self.packet_clicked;
                var from_to_data = from_to + 'from=' + dates_list[0] + '&to=' + dates_list[1] + '&project=' + self.project
                       + '&center=' + self.location + '&type=' + 'day' + final_work;
                $('.day2').addClass('active btn-success');
                $('.day2').siblings().removeClass('active btn-success');
                //self.main_render(from_to_data)

               $http({method:"GET", url:from_to_data}).success(function(result){

                        self.drop_list = [];
                        self.drop_list =  result.result.drop_value;

                        for (var sub_pro in self.drop_list) {
                            self.sub_pro_sel.options[self.sub_pro_sel.options.length] = new Option(sub_pro, sub_pro);
                        }
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
                                //self.wor_pac_sel.selectedIndex=1;
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

                            $('#select').val(self.start + ' to ' + self.end)
                            self.sel_type = result.result.days_type;
                            if (self.sel_type === 'week'){
                                $('.week2').addClass('active btn-success');
                                $('.week2').siblings().removeClass('active btn-success');
                            }
                            if (self.sel_type === 'month'){
                                $('.month2').addClass('active btn-success');
                                $('.month2').siblings().removeClass('active btn-success');
                            }
                            if (self.sel_type === 'day'){
                                $('.day2').addClass('active btn-success');
                                $('.day2').siblings().removeClass('active btn-success');
                            }
                            self.chart_render(result,self.project,self.location);

                           if (self.sel_type === 'week'){
                                $('.week').addClass('active btn-success');
                                $('.week').siblings().removeClass('active btn-success');
                            }
                            if (self.sel_type === 'month'){
                                $('.month').addClass('active btn-success');
                                $('.month').siblings().removeClass('active btn-success');
                            }
                            if (self.sel_type === 'day'){
                                $('.day').addClass('active btn-success');
                                $('.day').siblings().removeClass('active btn-success');
                            }
                            self.chart_render(result,self.project,self.location); 
                         });
                 }); 

            }


            self.update_one = function(index,selected_name){
            var sub_pro = self.sel_pack[0];
            var sub_pac = self.sel_pack[1];
            var wor_pac = self.sel_pack[2];
            var final_work =  '&sub_project=' + sub_pro + '&sub_packet=' + sub_pac + '&work_packet=' + wor_pac
            var dateEntered = document.getElementById('select').value
            dateEntered = dateEntered.replace(' to ','to');
            var from = dateEntered.split('to')[0].replace(' ','');
            var to = dateEntered.split('to')[1].replace(' ','');
            var placeholder = ''
            var from_to_data = from_to + 'from=' + from + '&to=' + to + '&project=' + self.project
                   + '&center=' + self.location + '&type=' + self.day_type  + final_work;

            $http({method:"GET", url:from_to_data}).success(function(result){
                self.high_data_gener = [];
                var final_data_gener = result.result;
                self.high_data_gener.push(final_data_gener);
                            angular.extend(self.chartOptions, {
               xAxis: {
                 categories: self.high_data_gener[0].data.date,
                 title: {
                  text: '',
                 }
               },
               plotOptions: {
                series : {
                    allowPointSelect: true,
                    point: {
                        events:{
                            select: function(e) {
                            console.log(e.target.series.name);
                            var productivity_graph ='/api/chart_data/?'
                            $http.get( productivity_graph+ 'packet=' + e.target.series.name + '&date=' + e.target.category).success(
                            function(data, status)
                                {
                                    $('#myModal').modal('show');
                                    var names_list =  data.result;
                                    self.names = names_list;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});

                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].productivity_data
             });

                            angular.extend(self.chartOptions9_2.yAxis,{
                                min:result.result.min_external_time_line,
                                max:result.result.max_external_time_line
                            });
                            angular.extend(self.chartOptions9_2, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            series: self.high_data_gener[0].external_time_line
                            });
                            angular.extend(self.chartOptions9.yAxis,{
                                min:result.result.min_internal_time_line,
                                max:result.result.max_internal_time_line
                            });
                            angular.extend(self.chartOptions9, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            series: self.high_data_gener[0].internal_time_line
                            });

                            /*angular.extend(self.chartOptions19.yAxis,{
                                min:result.result.min_original_productivity_graph,
                                max:result.result.max_original_productivity_graph
                            });*/
                            angular.extend(self.chartOptions19, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            series: self.high_data_gener[0].original_productivity_graph
                            });
                            angular.extend(self.chartOptions20, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            series: self.high_data_gener[0].internal_pareto_graph_data
                            });

                            angular.extend(self.chartOptions21, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date,
                                title: {
                                    text: '',
                                }
                            },
                            series: self.high_data_gener[0].external_pareto_graph_data
                            });

                            angular.extend(self.chartOptions10, {
                            xAxis: {
                                categories: self.high_data_gener[0].data.date
                            },
                            series: self.high_data_gener[0].productivity_data
                            });
                            angular.extend(self.chartOptions4.yAxis.title,{
                                text: ''
                            });
                            angular.extend(self.chartOptions4.plotOptions.series.point.events,{
                select: function(e) {
                        console.log(e);
                        $("#perc_hello").html(e.target.name);
                        $("#perc_temp").html(e.target.y);
                        $('#percent_graph').modal('show');
                        }
              });
                            angular.extend(self.chartOptions4,{
              series: [{
                 name: 'accuracy',
                 colorByPoint: true,
                    data: self.high_data_gener[0].internal_accuracy_graph
             }]
             });
                            angular.extend(self.chartOptions4.yAxis,{
                                min:result.result.int_min_value,
                                max:result.result.int_max_value
                            })

                            angular.extend(self.chartOptions45,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].internal_sub_error_types
                                }]
                            });

                            angular.extend(self.chartOptions46,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].external_sub_error_types
                                }]
                            });

                            angular.extend(self.chartOptions5,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].internal_errors_types
                                }]
                            });

                            angular.extend(self.chartOptions23,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].internal_errors_types
                                }]
                            });

                            angular.extend(self.chartOptions5_2,{
                                series: [{
                                    name: '',
                                    colorByPoint: true,
                                    data: self.high_data_gener[0].external_errors_types
                                }]
                            });
angular.extend(self.chartOptions18, {
                                xAxis: {
                                    categories: self.high_data_gener[0].data.date,
                                    title: {
                                        text: '',
                                    }
                                },
                                plotOptions: {
                                    series : {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        point: {
                                            events:{
                                             select: function(e) {

                                             var addition = '&project=' +pro + '&center=' +loc;
                                             console.log(e.target.series.name);
                                             var productivity_graph ='/api/chart_data/?'
                                             var packet_clicked = e.target.series.name;
                                             var is_exist = packet_clicked.indexOf('&');
                                             if (is_exist > 0){
                                                packet_clicked = packet_clicked.replace(' & ',' and ')
                                             }
                            $http.get( productivity_graph+ 'packet=' + packet_clicked + '&date=' + e.target.category +
                            '&type=' + 'Production Trends' + addition).success(
                            function(data, status)
                                {

                                    $('#myModal').modal('show');
                                    self.names = data.result.data;
                                    self.fields_list_drilldown = self.list_object_drilldown[data.result.type];
                                    self.chart_type = data.result.type;
                                    console.log(self.names);
                                }).error(function(error){ console.log("error")});

                        }
                    }
                    }
                },
                bar: {
                 dataLabels: {
                 enabled: true
                 }
                }
               },
               series: self.high_data_gener[0].productivity_data
             });
                            angular.extend(self.chartOptions6.yAxis.title,{
                                text: ''
                            });
                            angular.extend(self.chartOptions6.plotOptions.series.point.events,{
                                select: function(e) {
                        console.log(e);
                        $("#perc_hello").html(e.target.name);
                        $("#perc_temp").html(e.target.y);
                        $('#percent_graph').modal('show');
                        }
                            });
                            angular.extend(self.chartOptions6,{
              series: [{
                 name: 'accuracy',
                 colorByPoint: true,
                    data: self.high_data_gener[0].external_accuracy_graph
             }]
             });
                            angular.extend(self.chartOptions6.yAxis,{
                                min:result.result.ext_min_value,
                                max:result.result.ext_max_value
                            });
                            });
            }

            $http({method:"GET", url:drop_down_link}).success(function(result){
                angular.extend(self.packet_hierarchy_list, result.result.level);
             })

            self.chartOptions = {
                chart : {
                 backgroundColor: "transparent"
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
            /*self.chartOptions10 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent"
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
            };*/

           self.chartOptions39 = {
                chart : {
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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
            };

            self.chartOptions9 = {
                chart : {
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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
                    type: 'pie'
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
                    type: 'pie'
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


            self.chartOptions5 = {
                chart: {
                    backgroundColor: "transparent",
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
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
                    type: 'pie'
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
                    type: 'pie'
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
                backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                //text: 'Cumulative %',
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                //text: 'Error Count',
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
                //text: 'Cumulative %',
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                //text: 'Error Count',
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
                //text: 'Cumulative %',
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Cumulative %',
                //text: 'Error Count',
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
                 backgroundColor: "transparent"
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
                //text: 'Cumulative %',
                text: 'Error Count',
                color:'a2a2a2',
            }
        }, { // Secondary yAxis
            gridLineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: 'Cumulative %',
                //text: 'Error Count',
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
                 backgroundColor: "transparent"
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

            self.chartOptions15_2 = {
                chart : {
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
            self.chartOptions16_2 = {
                chart : {
                 backgroundColor: "transparent"
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
            self.chartOptions17 = {
            chart: {
                type: 'column',
                backgroundColor: "transparent"
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

            self.chartOptions18 = {
                chart : {
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                 backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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
                backgroundColor: "transparent"
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

    self.chartOptions22 = '<p> workpacket </p>'



            //self.hideLoading();
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
