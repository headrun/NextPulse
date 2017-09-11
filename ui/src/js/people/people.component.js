;(function (angular) {
  "use strict";

  angular.module("people")
         .component("people", {

           "templateUrl": "/js/people/people.html",
           "controller": ['$http','$scope','$rootScope',


           function ($http, $scope, $rootScope) {

                var vm = this;
                var people_data = '/pd/get_sla_data';
                var people_data_2 = '/pd/get_peoples_data';
                vm.render_chart_from_url = function(url, name) {
                    vm.chart_name = name;

                    $http({method:"GET", url: url}).success(function(result){

                      if (vm.chart_name == 'Productivity') {
                        var main_data = result.result.original_productivity_graph;    
                        var date_list = result.result.date;
                      }

                      if (vm.chart_name == 'Target Achieved') {

                        var main_data = result.result.productivity_data;
                        var date_list = result.result.data.date;      
                      }
                      
                      if (vm.chart_name == 'Internal Accuracy') {

                        var main_data = result.result.internal_time_line;
                        var date_list = result.result.date;
                      }    

                      if (vm.chart_name == 'External Accuracy') {

                        var main_data = result.result.external_time_line;
                        var date_list = result.result.date; 
                      }

                      if (vm.chart_name == 'TAT') {
                        
                        var main_data = result.result.tat_graph_details;
                        var date_list = result.result.date;
                      }
                      if (vm.chart_name == 'FTE Utilisation') {

                         var main_data = result.result.utilization_fte_details;
                         var date_list = result.result.date;
                       }  

                      if (vm.chart_name == 'Operational Utilisation') {

                          var main_data = result.result.utilization_operational_details;  
                          var date_list = result.result.date;  
                       }  


                    $('.widget-content').removeClass('widget-loader-show');
                    $('.widget-body').removeClass('widget-data-hide');

                    angular.extend(vm.widget_data, {

                        xAxis: {
                            categories: date_list,
                        },  
                        series: main_data

                    });
                    
                  });  
             }


               vm.get_popup = function(data, type, month, name, target) {
                  vm.month_to_display = data[month];
                  vm.widget_type = type;
                  vm.widget_name = name;
                  vm.project_to_display = data.project;
                  vm.center_to_display = data.center;
                  vm.target_to_display = data.color[target][1];
                  vm.key_of_table = data.color[target][2];
                  $('#extra-table').hide();
                  $('#extra-table2').hide();
                  if (name == "Productivity"){
                      $('#extra-table2').show();
                      var pop_url_target = '/pd/get_individual_target?core_key='+vm.key_of_table;

                      $http({method:"GET", url: pop_url_target}).success(function(result){
                         var big_object = result.result;
                         var all_keys = Object.keys(result.result);
                         var all_packets = []; 

                         for (var i=0; i<all_keys.length; i++){

                             all_packets.push(all_keys[i].split('_')[4]);
                         }   

                         function onlyUnique(value, index, self) { 
                             return self.indexOf(value) === index;
                         }   

                         var packets = all_packets.filter( onlyUnique );
                         var fin_ind = packets.indexOf('final');
                         packets.splice(fin_ind, 1); 
                         var prod_ind = packets.indexOf('prod');
                         packets.splice(prod_ind, 1); 
                         var bill_ind = packets.indexOf('bill');
                         packets.splice(bill_ind, 1); 
                         var main_table_data = [];
                         var main_table_data2 = [];
                         for (var j=0; j<packets.length; j++){
                             var main_obj = {'packet':'', 'days':'', 'fte_age':'', 'volume':'', 'productivity':''};
                             main_obj.packet = packets[j];
                             var key = vm.key_of_table+'_target_'+packets[j]+'_';
                             //main_obj.fte_age = big_object[key+'no_of_agents'];
                             main_obj.days = big_object[key+'no_of_days'];
                             main_obj.fte_age = big_object[key+'no_of_agents'];
                             main_obj.volume = big_object[key+'actual'];
                             main_obj.productivity = big_object[key+'prod_uti'];
                             main_table_data.push(main_obj);
                            }
                         vm.main_data2 = main_table_data;
                         var main_obj2 = {'finalPeople':'', 'finalVolume':'', 'finalProduct':''};
                         var key1 = vm.key_of_table+'_target_';
                         main_obj2.finalPeople = big_object[key1+'bill_ppl'];
                         main_obj2.finalVolume = big_object[key1+'final_actual'];
                         main_obj2.finalProduct = big_object[key1+'prod_utility'];
                         main_table_data2.push(main_obj2);
                         vm.main_data3 = main_table_data2;
                      });
                    
                  }
                  if (name == "Target Achieved"){
                      $('#extra-table').show();

                      //var key_to_ajax = data.color[target][2];
                      var pop_url_target = '/pd/get_individual_target?core_key='+vm.key_of_table;

                      $http({method:"GET", url: pop_url_target}).success(function(result){
                         var big_object = result.result;
                         var all_keys = Object.keys(result.result);
                         var all_packets = [];

                         for (var i=0; i<all_keys.length; i++){

                             all_packets.push(all_keys[i].split('_')[4]);
                         }

                         function onlyUnique(value, index, self) { 
                             return self.indexOf(value) === index;
                         }

                         var packets = all_packets.filter( onlyUnique );
                         var fin_ind = packets.indexOf('final');
                         packets.splice(fin_ind, 1);
                         var prod_ind = packets.indexOf('prod');
                         packets.splice(prod_ind, 1);
                         var bill_ind = packets.indexOf('bill');
                         packets.splice(bill_ind, 1); 
                         var main_table_data = [];
                         var main_table_data2 = [];
                         for (var j=0; j<packets.length; j++){
                             var main_obj = {'packet': '', 'target': '', 'noFTE': '', 'noDays': '', 'actual': '', 'pacTarget':'', 'percentage': ''};
                             main_obj.packet = packets[j];
                             var key = vm.key_of_table+'_target_'+packets[j]+'_';
                             main_obj.target = big_object[key+'single_target'];
                             main_obj.noFTE = big_object[key+'no_of_agents'];
                             main_obj.noDays = big_object[key+'no_of_days'];
                             main_obj.actual = big_object[key+'actual'];
                             main_obj.pacTarget = big_object[key+'target'];
                             main_obj.percentage = big_object[key+'prod_percen'];
                             main_table_data.push(main_obj);
                         }
                         vm.main_data = main_table_data;
                         var main_obj2 = {'finalactual':'', 'finaltarget':'', 'finalproductivity': ''};
                         var key1 = vm.key_of_table+'_target_';
                         main_obj2.finalactual = big_object[key1+'final_actual'];
                         main_obj2.finaltarget = big_object[key1+'final_target'];
                         main_obj2.finalproductivity = big_object[key1+'final_product_val'];
                         main_table_data2.push(main_obj2);
                         vm.main_data4 = main_table_data2;
                      });

                  }

                  $('.widget-content').addClass('widget-loader-show');
                  $('.widget-body').addClass('widget-data-hide');
                  vm.date_mapping = {'August': '2017-08-01',
                                     'July': '2017-07-01',
                                     'June': '2017-06-01',
                                     'May': '2017-05-01'
                                    };

                  vm.start_date = vm.date_mapping[vm.month_to_display];

                  var date_obj = new Date(vm.start_date);
                  var firstDay = new Date(date_obj.getFullYear(), date_obj.getMonth(), 1);
                  var lastDay = new Date(date_obj.getFullYear(), date_obj.getMonth() + 1, 0);

                  vm.end_date = '';
                  vm.end_date += lastDay.getFullYear() +'-';
                  vm.end_date += lastDay.getMonth()+1+'-';
                  vm.end_date += lastDay.getDate();
                  vm.chart_name = name;
                  vm.day_type = function(type) {
                    
                  $('.widget-content').addClass('widget-loader-show');
                  $('.widget-body').addClass('widget-data-hide');
                    var url_to = '/api/'+vm.widget_type+'/?&project='+vm.project_to_display+
                          '&center='+vm.center_to_display+'&from='+vm.start_date+'&to='+vm.end_date+'&type='+
                          type+'&is_clicked='+type+'_yes';
                        vm.render_chart_from_url(url_to, vm.widget_name);

                        if (type === 'day') {
                            $('.day').addClass('active btn-success');
                            $('.day').siblings().removeClass('active btn-success');
                        }

                        if (type === 'week') {
                            $('.week').addClass('active btn-success');
                            $('.week').siblings().removeClass('active btn-success');
                        }

                        if (type === 'month') {
                            $('.month').addClass('active btn-success');
                            $('.month').siblings().removeClass('active btn-success');
                        }
                    }
                    
                    if (vm.widget_name === 'Productivity') {
                        $('#perce').hide();
                    }
                    else {
                       $('#perce').show(); 
                    }

                    vm.url = '/api/'+vm.widget_type+'/?&project='+vm.project_to_display+
                        '&center='+vm.center_to_display+'&from='+vm.start_date+'&to='+vm.end_date+'&type=week';
                    vm.render_chart_from_url(vm.url, vm.widget_name);
                    
                    $('.week').addClass('active btn-success');
                    $('.week').siblings().removeClass('active btn-success');
                    $('#people_pop').modal('show');
                }

              vm.widget_data = {
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


                $http({method:"GET", url:people_data}).success(function(result){

                  vm.data = result.result;
                  vm.center_data_1 = result.center_total;

               });

                $http({method:"GET", url:people_data_2}).success(function(result){
                  vm.data_2 = result.result;
                  vm.center_data2 = result.center_total;
                  //debugger;
               });

           }],

            "bindings": {

              "hideLoading": "&",
              "showLoading": "&",
              "updateState": "&"
            }
         });

}(window.angular));
