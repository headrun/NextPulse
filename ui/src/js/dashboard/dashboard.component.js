;(function (angular) {
  "use strict";

  // Decalare Pages that are available in this component
  var pages = {
                 "page1": {

                   "name"    : "page1",
                   "fullName": "dashboard.page1",
                   "text"    : "Page 1",
                   "state"   : {},
                   "stateStr": "{}"
                 },
                 "landing": {

                   "name"    : "landing",
                   "fullName": "dashboard.landing",
                   "text"    : "landing",
                   "state"   : {},
                   "stateStr": "{}"
                 },
                 "page3": {

                   "name"    : "page3",
                   "fullName": "dashboard.page3",
                   "text"    : "Page 3",
                   "state"   : {},
                   "stateStr": "{}"
                 }
              };

  var sharedProps = [{"name": "show-loading", "value": "$ctrl.showLoading()"},
		     {"name": "hide-loading", "value": "$ctrl.hideLoading()"},
		     {"name": "tab-data", "value":"$ctrl.tab"}];

  // If one uses a menu bar, the order of appearance is here
  var pagesOrder = ["landing", "page1", "page3"];

  var stre = 'Hello';

  angular.module("dashboard")
         .component("dashboard", {

           "templateUrl": "/js/dashboard/dashboard.html",
           "controller" : ["Session", "$state", "$rootScope",

             function (Session, $state, $rootScope) {

               var stateName = $state.current.name.split(".")[1];

               var that = this;

               // Storing user data in scope
               this.user = Session.get();


               // Loading scree will be shown when its true
               this.isLoading = true;

               this.showLoading = function () {

                 this.isLoading = true;
               };

               this.hideLoading = function () {

                 this.isLoading = false;
               };

               this.pages = pages;
               this.pagesOrder = pagesOrder;
               this.selectDropdown = function(str) {

               }

               this.selectedValue = stre;

               // Update URL without refresh (maintaining state in URL)
               function updateUrl (pageName) {

                 $state.go("dashboard." + pageName,
                           {"state" : that.pages[pageName].stateStr},
                           {"notify": false});
               }

               // The current page that is being displayed
               this.activePage = this.pagesOrder[0];

               this.setActivePage = function (pageName) {

                 this.activePage = pageName;
               };

               // Update the state of the page, and also the URL
               this.updateState = function (pageName, state) {

                 state = state || {};
                 this.tab = this.pages[pageName];
                 if (this.tab != undefined)
                  this.tab.state = state;
                 this.tab.stateStr = JSON.stringify(state);

                 this.setActivePage(pageName);
                 updateUrl(pageName);

               };

               // on navigation, update the state of current page
               function onNavigation (event, next, params) {

                 if (next.name !== "dashboard") {

                   that.updateState(next.name.split(".")[1],
                                    JSON.parse(params.state || "{}"));
                 }
               }

               var bindedEvents = [];

               function bindEvents () {

                 bindedEvents.push($rootScope.$on("$stateChangeStart", onNavigation));
               }

               function unbindEvents () {

                 angular.forEach(bindedEvents, function (unbindFunc) {

                   unbindFunc();
                 });
               }

               this.$onInit = bindEvents;

               this.$onDestroy = unbindEvents;

               if (!stateName) {

                 $state.go("dashboard." + this.pagesOrder[0]);
                 return;
               }

               // Update the state of current page when the component is rendered

               this.updateState(stateName,
                                JSON.parse($state.params.state || "{}"));
               this.selectDropdown(stre);

             }]
         });

         angular.module("dashboard")
                .config(["$locationProvider", "$stateProvider",
                  "$httpProvider", "$urlRouterProvider",

           function ($lp, $sp, $hp, $urp) {

             angular.forEach(pagesOrder, function (page) {

	       var template = "<" + page + " ";

	       angular.forEach(sharedProps, function (prop) {

	         template += prop.name + "=" + "\""+ prop.value +"\"";
	       });

               template += "></" + page + ">";

               $sp.state("dashboard." + page, {

                 "url"     : page + (page === "page1" ? "/*selpro" : "" ),
                 "template": template,
                 "authRequired": true
               });
             });

             $urp.otherwise(pagesOrder[0]);
           }
         ]);
}(window.angular));
