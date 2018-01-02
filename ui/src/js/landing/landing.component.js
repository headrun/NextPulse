;(function (angular) {
  "use strict";

  angular.module("landing")
         .component("landing", {

           "templateUrl": "/js/landing/landing.html",
           "controller": ['$http','$scope','$rootScope',

           function ($http,$scope,$rootScope) {

             var self = this;

             $rootScope.sel_value = '';

             var project = 'api/project/';

             self.hideLoading();

             $scope.check = $rootScope.check;

             $scope.check_url = $rootScope.check_url;

              self.clickPro = function(val, $rootScope){

                self.showLoading();

                $('#dropdown_title').text(val.split(' - ')[1]);

              }
            $http({method:"GET", url:project}).success(function(result){

                if (result.result['role'] == "customer") {

                    var map_list = result.result.list;

                    if (map_list.includes("none")) {

                        self.mapping_list = []

                        var map_list = map_list[1];

                        self.mapping_list.push(map_list);

                    }

                    else {

                        self.mapping_list = map_list;
                    }
                    
                    if ((self.mapping_list.length == 1) && ($scope.check == undefined)) {

                        window.location = "#!/page1/"+self.mapping_list[0];

                    } else if ($scope.check == 1) {

                        window.location = $scope.check_url;
                        
                      } else {
                            self.mapping_list;
                       }
                }

                if (result.result.role == "team_lead") {

                    self.mapping_list = []

                    self.mapping_list.push(result.result.list[1]);

                    if ((self.mapping_list.length == 1) && ($scope.check == undefined)) {

                        self.showLoading();

                        window.location = "#!/page1/"+self.mapping_list[0];

                    } else if ($scope.check == 1) {

                        window.location = $scope.check_url;

                    } else {
                        
                           self.mapping_list; 
                    }
                }

                if (result.result['role'] == "center_manager") {

                    var map_list = result.result.list;

                    self.mapping_list = map_list;

                    if ((self.mapping_list.length == 1) && ($scope.check == undefined)) {

                        window.location = "#!/page1/"+self.mapping_list[0];

                    } else if ($scope.check == 1) {
                        
                          window.location = $scope.check_url;

                    } else {

                        self.mapping_list;

                    }
                 }

                if (result.result['role'] == "nextwealth_manager") {

                    var map_list = result.result.list;

                    self.mapping_list = map_list.sort();

                    $('.mythili').show();

                    //$scope.check = $rootScope.check;
                    //$scope.check_url = $rootScope.check_url;

                    if (self.mapping_list.length == 1) {

                        window.location = "#!/page1/"+self.mapping_list[0];

                    } else if ($scope.check == 1) {
                            window.location = $scope.check_url;   
                        }
                       else {
                            self.mapping_list;   
                        } 
                    }
            });

             self.widgets_list = '';
             self.widgets_names = [];

         }],

            "bindings": {

              "hideLoading": "&",
              "showLoading": "&"
            }
         }); 
 
}(window.angular));
