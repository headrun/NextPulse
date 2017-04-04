;(function (angular) {
  "use strict";

  angular.module("logout")
         .component("logout", {

           "templateUrl": "/js/logout/logout.html",
           "controller" : ["$rootScope",
                           "Auth", "AUTH_EVENTS",
             function ($rootScope, Auth, AUTH_EVENTS) {

               this.logout = function () {

                 Auth.logout().then(function () {

                   $rootScope.$broadcast(AUTH_EVENTS.logoutSuccess);
                 });
               };
             }
           ]
         });

}(window.angular));
