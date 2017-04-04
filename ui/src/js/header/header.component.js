;(function (angular) {
  "use strict";

  angular.module("header")
         .component("header", {
           "templateUrl": "/js/header/header.html",
           "controller" : ["$rootScope", "$state", "$filter", "$interval","$http", "Session",

             function ($rootScope, $state, $filter, $interval , $http, Session) {

               var self = this;

               this.user = Session.get();

                if (this.user.roles.indexOf("team_lead") >= 0) {
                    this.user.role = "Team Lead";
                }
                if (this.user.roles.indexOf("customer") >= 0) {
                    $('#admin_but').hide();
                    this.user.role = "Customer";
                }
                if (this.user.roles.indexOf("center_manager") >= 0) {
                    $('#fileupload').hide();
                    $('#admin_but').hide();
                    this.user.role = "Center Manager";
                }
                if (this.user.roles.indexOf("nextwealth_manager") >= 0) {
                    $('#fileupload').hide();
                    $('#admin_but').hide();
                    this.user.role = "Nextwealth Manager";
                }
                if (this.user.role == "Customer") {
                    $('#fileupload').hide();
                }
                if (this.user.role == "Team Lead") {
                    $('#select_dropdown').hide();
                    $('#home').hide();
                }
               this.collapsed = false;

               this.toggleCollapse = function () {

               this.collapsed = !this.collapsed;
               }
              var project = 'api/project/';
              self.clickFun = function(val){
                console.log('Yesh clicked');
                self.cen_pro_name['state'] = val;
                val = '';
                self.updateState({'state':self.cen_pro_name, 'pageName':'page1'});
              }

                self.onChange = function(page) {
                    location.href = '#!'+page;
                }


              $http({method:"GET", url:project}).success(function(result){

                if (result.result.role == "customer") {
                    if (result.result.list[0] == "none") {
                        $('#select_dropdown').hide();
                    }
                    var map_list = result.result.list;
                    self.mapping_list = map_list;
                    if (result.result.list[0] != "none"){
                        var option = map_list[1];
                        self.select_option = option.split(' - ')[1];
                    }
                }
                if (result.result['role'] == "center_manager")
                    {
                    var map_list = result.result.list;
                    self.mapping_list = map_list;
                    var option = map_list[1];
                    self.select_option = option.split(' - ')[1];
                    }

                if (result.result['role'] == "nextwealth_manager")
                    {
                    var map_list = result.result.list;
                    self.mapping_list = map_list;
                    if (self.mapping_list.length > 1){
                             var option = map_list[1];
                             self.select_option = option.split(' - ')[1];
                        }
                    else{
                        self.select_option = map_list[0].split(' - ')[1];
                        }
                    }


              });
              self.project_name = '';
              self.proj_list = '';
              self.center = '';
              self.ppp = '';
              self.mapping_list = '';
              self.select_option = '';
              self.center_list = [];
              self.cen_pro_name = {};
             }
           ],
           "bindings": {
             "tabsOrder"  : "<",
             "tabs"       : "<",
             "activeTab"  : "<",
             "updateState": "&",
             "selectedValue": "=",
             "selectDropdown": "&"
           }
         });
}(window.angular));
