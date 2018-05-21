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
              $('.modal-content').removeClass('widget-loader-show');

              that.forgot_pass = function(mail_id) {
                 $('.modal-content').addClass('widget-loader-show');
                 $http({method:"GET", url:'/api/forgot_password/?email='+mail_id}).success(function(result){
                   if (result.result === 'Cool') {
                     $('.modal-content').removeClass('widget-loader-show');
                     that.pass_reset = true;
                   }
                   if (result.result === 'Email id not found') {
                     $('.modal-content').removeClass('widget-loader-show'); 
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
