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

              $("#forgotpassModal").on("hidden.bs.modal", function() {
                $('.reset').hide();
                $('#err-msg').hide();
                $('form')[1].reset();
                $("#reset-btn").removeAttr("disabled");
              });

              that.forgot_pass = function(mail_id) {
                 $('.modal-content').addClass('widget-loader-show');
                 $http({method:"GET", url:'/api/forgot_password/?email='+mail_id}).success(function(result){
                   if (result.result === 'Cool') {
                     $('.modal-content').removeClass('widget-loader-show');
                     that.pass_reset = true;
                    $("#err-msg").hide();
                    $("#reset-btn").attr("disabled","disabled");
                   }
                   if (result.result === 'Email id not found') {
                     $('.modal-content').removeClass('widget-loader-show'); 
                     that.pass_reset = false;
                    $("#err-msg").show();
                    that.mailid_mes = "Above Email id is not linked with your login";
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

                Auth.login(credentials).then(function (data,err) {
                  
                  $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                }, function (data,err) {
                  that.loadingText = "Submit";
                  that.errorMsg = data.data.msg;
                  that.viewSubmit = "";
                  
                  swal("Nextpulse Says", data.data.msg, "error");
                });
              };
            }]
        });

}(window.angular));

