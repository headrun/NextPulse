;(function (angular) {
  "use strict";

  // If User is not logged in, he will be redirected to LOGIN_STATE
  var LOGIN_STATE = "login",

      // Once the user is logged in using the form he will be redirected
      // to LOGIN_REDIRECT_STATE
      LOGIN_REDIRECT_STATE = "dashboard";

  angular.module("bootstrap")
         .config(["$locationProvider", "$stateProvider",
                  "$httpProvider", "$urlRouterProvider",

           function ($lp, $sp, $hp, $urp) {

             $lp.hashPrefix('!');

             /* ALL YOUR CONFIG GOES HERE */

             $sp.state("login", {

               "url"     : "/login",
               "template": "<login></login>"
             }).state("dashboard", {

               "url"     : "/",
               "template": "<dashboard></dashboard>",

               /*
                * If authRequired is true,
                * login check will be done before loadin the page
                * if not authenticated, he will be redirected to LOGIN_PAGE
               */
               "authRequired": true
             }).state("reset_password", {
               "url"     : "/reset/:userId/:authKey",
               "template": "<reset></reset>"
             }).state("review", {
               "url"     : "/review",
               "template": "<review></review>",
               "authRequired": true
             }).state("people", {
               "url"     : "/people",
               "template": "<people></people>"
             });

             $urp.otherwise("/");

             $hp.defaults.xsrfCookieName = "csrftoken";
             $hp.defaults.xsrfHeaderName = "X-CSRFToken";
           }
         ]).run(["$rootScope", "$state",
                 "Auth", "AUTH_EVENTS",

          function ($rootScope, $state, Auth, AUTH_EVENTS) {

            // DO NOT EDIT THIS FUNCTION

            var skipAsync = false;

            $rootScope.$on("$stateChangeStart", function (event, next, params) {

              if (skipAsync) {

                skipAsync = false;
                return;
              }

              if (next.authRequired) {

                event.preventDefault();

                ;(function (thisNext) {

                  Auth.status().then(function (resp) {

                    if (thisNext.name !== next.name) {

                      return;
                    }

                    if (!resp.user) {

                      $rootScope.$broadcast(AUTH_EVENTS.unAuthorized);
                      return;
                    }

                    skipAsync = true;
                    $state.go(thisNext.name, params);
                  });
                }(next, params));
              }
            });

            if (window.location.href.indexOf('page1') > 0) {
                var host = window.location.host;
                var hash = window.location.hash;
                self.landing_url = 'http://'+ host + '/' + hash;
            }

            $rootScope.$on(AUTH_EVENTS.loginSuccess, function () {

              $state.go(LOGIN_REDIRECT_STATE, {"location": "replace"});

            });

            function goToLogin () {
            if (window.location.href.indexOf('reset_password') > 0){
              $state.go('reset_password', {});
            }
            else {
              $state.go(LOGIN_STATE, {"location": "replace"});
                if (window.location.href.indexOf('page1') > 0) {
                  $rootScope.check_url = self.landing_url;  
                  $rootScope.check = 1;
                }
              }   
            }

            $rootScope.$on(AUTH_EVENTS.unAuthorized, goToLogin);
            $rootScope.$on(AUTH_EVENTS.logoutSuccess, goToLogin);
          }
         ]);
}(window.angular));
