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


                vm.get_popup = function(data, type, month) {

                  vm.month_to_display = data[month];
                  vm.widget_type = type;
                  vm.project_to_display = data.project;
                  vm.center_to_display = data.center;

                  vm.url = '/api/'+vm.widget_type+'/?&project='+vm.project_to_display+
                        '&center='+vm.center_to_display+'&from=2017-05-01&to=2017-05-31&type=week';

                  $http({method:"GET", url: vm.url}).success(function(result){

                    debugger;
                  })

                  //vm.updateState({'state': vm.data_for_widget, 'pageName':'page1'});

                  $('#people_pop').modal('show');
                }

                vm.widget_data = {

                    yAxis: {
                        title: {
                            text: 'Number of Employees'
                        }
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'middle'
                    },

                    plotOptions: {
                        series: {
                            pointStart: 2010
                        }
                    },

                    series: [{
                        name: 'Installation',
                        data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
                    }, {
                        name: 'Manufacturing',
                        data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
                    }, {
                        name: 'Sales & Distribution',
                        data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
                    }, {
                        name: 'Project Development',
                        data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
                    }, {
                        name: 'Other',
                        data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
                    }]

                };

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
