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

                      if (vm.chart_name == 'Production') {

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


                      /*if (vm.chart_name == 'Internal Accuracy') {
                        //var main_data = result.result.internal_accuracy_graph;
                        angular.extend(vm.widget_acc_data,{

                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.internal_accuracy_graph
                               }],  

                        });

                      }*/
                    //$("#data-show").show();
                    $('.widget-content').removeClass('widget-loader-show');
                    $('.widget-body').removeClass('widget-data-hide');

                    angular.extend(vm.widget_data, {

                        xAxis: {
                            categories: date_list,
                        },  
                        series: main_data

                    });
                    
                    /*if (vm.chart_name == 'Internal Accuracy') {
                        angular.extend(vm.widget_acc_data,{

                               series: [{
                                   name: 'accuracy',
                                   colorByPoint: true,
                                   cursor: 'pointer',
                                   data: result.result.internal_accuracy_graph
                               }],  

                        });
                    }*/
                    //$('.widget-content').removeClass('widget-loader-show');
                  });  
             }

               /*vm.graph_rend = function(main_data, date_list) {

                    angular.extend(vm.widget_data, {

                      xAxis: {
                        categories: date_list,
                      },
                      series: main_data

                    });    
                }*/ 

               vm.get_popup = function(data, type, month, name, target) {
                  vm.month_to_display = data[month];
                  vm.widget_type = type;
                  vm.widget_name = name;
                  vm.project_to_display = data.project;
                  vm.center_to_display = data.center;
                  vm.target_to_display = data.color[target][1];
                
                  $('.widget-content').addClass('widget-loader-show');
                  $('.widget-body').addClass('widget-data-hide');
                  //$("#people_pop").empty();  
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
                    /*if (vm.chart_name != 'Internal Accuracy') {
                        vm.url = '/api/'+vm.widget_type+'/?&project='+vm.project_to_display+
                            '&center='+vm.center_to_display+'&from=2017-05-01&to=2017-05-31&type=week';
                        vm.render_chart_from_url(vm.url, vm.widget_name);
                    }
                    if (vm.chart_name == 'Internal Accuracy') {
                        var url_acc = '/api/'+vm.widget_type+'/?&project='+vm.project_to_display+
                              '&center='+vm.center_to_display+'&from=2017-05-01&to=2017-05-31&type=day';
                        vm.render_chart_from_url(url_acc, vm.widget_name);
                    }*/
                    vm.url = '/api/'+vm.widget_type+'/?&project='+vm.project_to_display+
                        '&center='+vm.center_to_display+'&from='+vm.start_date+'&to='+vm.end_date+'&type=week';
                    vm.render_chart_from_url(vm.url, vm.widget_name);
                    
                    $('.week').addClass('active btn-success');
                    $('.week').siblings().removeClass('active btn-success');
                    $('#people_pop').modal('show');
                    //$("#data-show").hide();
                    //$('.widget-content').addClass('widget-loader-show');
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

          /*vm.widget_acc_data = {
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
            };*/
 

                $http({method:"GET", url:people_data}).success(function(result){

                  vm.data = result.result;

               });

                $http({method:"GET", url:people_data_2}).success(function(result){

                  vm.data_2 = result.result;

               });

           }],

            "bindings": {

              "hideLoading": "&",
              "showLoading": "&",
              "updateState": "&"
            }
         });

}(window.angular));
