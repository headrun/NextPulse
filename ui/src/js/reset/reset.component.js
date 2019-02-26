;(function (angular) {
  "use strict";

  angular.module("reset")
         .component("reset", {

           "templateUrl": "/js/reset/reset.html",
           "controller": ['$http','$scope','$rootScope','$stateParams', 

           function ($http,$scope,$rootScope,$stateParams) {

             var self = this;

             self.user_id = $stateParams.userId;
             self.auth_key = $stateParams.authKey;
             self.reset_status = false;
             self.pass_error = false;

             self.password = function(new_pa, new_again){

                 if (new_pa === new_again){

                   var data = $.param({
                     json: JSON.stringify({
                       name: new_pa,
                       user_id: self.user_id,
                       auth_key: self.auth_key
                     })
                   });

                   $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                   $http.post('api/change_password/', data).then(function(result){
                     if (result.statusText == 'OK') {
                      self.reset_status = true;
                      self.pass_error = false;
                     }
                   });
                 }
                 else {
                   self.pass_error = true;
                 }
             }

         }],

            "bindings": {

              "hideLoading": "&",
              "showLoading": "&"
            }
         });

}(window.angular));
