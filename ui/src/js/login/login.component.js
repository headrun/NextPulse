;(function (angular) {
  "use strict";

  angular.module("login")
         .component("login", {

           "templateUrl" : "/js/login/login.html",
           "controller"  : ["$rootScope", "Auth", "AUTH_EVENTS", "$http",

             function ($rootScope, Auth, AUTH_EVENTS, $http) {

              var that = this;
              that.email_id = '';
              that.pass_reset = false;
              that.mailid_mes == '';

              that.forgot_pass = function(mail_id) {
                 $http({method:"GET", url:'/api/forgot_password/?email='+mail_id}).success(function(result){
                   if (result.result === 'Cool') {
                     that.pass_reset = true;
                   }
                   if (result.result === 'Email id not found') {
                     that.mailid_mes = result.result;
                   }
                 })
              };

              this.credentials = {

                "username": "",
                "password": ""
              };

              this.errorMsg = "";
              this.loadingText = "Submit";

              this.onSubmit = function (credentials) {

                this.loadingText = "Verifying...";
                this.viewSubmit = "disabled";

                Auth.login(credentials).then(function () {

                  $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                }, function () {

                  that.loadingText = "Submit";
                  that.errorMsg = "Invalid Credentials";
                  that.viewSubmit = "";
                });
              };
            }]
        });

}(window.angular));
