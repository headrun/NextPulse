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


                $http({method:"GET", url:people_data}).success(function(result){    
    
                  vm.data = result.result;

               }); 

                $http({method:"GET", url:people_data_2}).success(function(result){    
    
                  vm.data_2 = result.result;

               }); 

           }], 
 
            "bindings": {

              "hideLoading": "&",
              "showLoading": "&" 
            }   
         }); 

}(window.angular));

