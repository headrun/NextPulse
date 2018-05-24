;(function (angular) {
  "use strict";

  angular.module("header")
         .component("header", {
           "templateUrl": "/js/header/header.html",
           "controller" : ["$rootScope", "$state", "$filter", "$interval","$http", "Session",

             function ($rootScope, $state, $filter, $interval , $http, Session) {

               var self = this;

               this.user = Session.get();

               self.new_password = '';
               self.new_again = '';
               self.pass_status = false;
               self.pass_error = false;

               self.change_href = function(item) {
                 $state.go("dashboard.page1",{'selpro': item});
               }

               self.agent_data = [
                  { Name: "Madhu Priya", value: "45", Name1: "Pavithra S", value1: "60", Name2: "Pavithra S", value2: "80"},
                  { Name: "Natasha", value: "38", Name1: "Natasha", value1: "45", Name2: "Natasha", value2: "67"},
                  { Name: "Dhanyalakshmi S", value: "30", Name1: "Maheswari M", value1: "28", Name2: "Maheswari M", value2: "49"},
                  { Name: "Dharani G K", value: "20", Name1: "Madhu Priya", value1: "15", Name2: "Madhu Priya", value2: "38"},
                  { Name: "Gomathi K", value: "10", Name1: "Pramila E", value1: "10", Name2: "Pramila E", value2: "12"},
                  ];

               self.packet_data = [
                  { Packet: "Latin America", value: "100", Packet1: "North America", value1:"90", Packet2: "Australia", value2:"80"},
                  { Packet: "Europe", value: "90", Packet1: "Arabia", value1: "80", Packet2: "India and Sri Lanka", value2: "70"},
                  { Packet: "DCIW Arabia", value: "90", Packet1: "Africa", value1: "80", Packet2: "Arabia", value2: "70"},
                  { Packet: "North America", value: "60", Packet1: "Arabia", value1: "70", Packet2: "India and Sri Lanka", value2: "50"},
                  { Packet: "Pakistan", value: "50", Packet1: "Quality Control", value1: "60", Packet2: "Arabia", value2: "35"},
               ]  
               
               self.password = function(new_pa, new_again_pa){
                 if (new_pa === new_again_pa){

                   var data = $.param({
                     json: JSON.stringify({
                       name: new_pa
                     })
                   });

                   $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                   $http.post('api/change_password/', data).then(function(result){
                     if (result.statusText == 'OK') {
                       self.pass_status = true;
                     }
                   });
                 }
                 else {
                   self.pass_error = true;
                 }
               }

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
                    $('#people').hide()
                    this.user.role = "Center Manager";
                }
                if (this.user.roles.indexOf("nextwealth_manager") >= 0) {
                    $('#fileupload').hide();
                    $('#admin_but').hide();
                    this.user.role = "Nextwealth Manager";
                }
                if (this.user.role == "Customer") {
                    $('#fileupload').hide();
                    $('#home').hide();
	                   $('#people').hide()			
                }
                if (this.user.role == "Team Lead") {
                    $('#select_dropdown').hide();
                    $('#home').hide();
		                $('#people').hide()	
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


                $('video').get(0).pause()

              $http({method:"GET", url:project}).success(function(result){

                if (result.result.role == "customer") {
                    if (result.result.list[0] == "none") {
                        $('#select_dropdown').hide();
                    }
                    var map_list = result.result.list;
                    self.mapping_list = map_list;
                    if (result.result.list[0] != "none"){
                        if ((result.result.list.length) == 2) {
                            var option = map_list[0];
                        }
                        else {
                        var option = map_list[1];
                        }
                        self.select_option = option.split(' - ')[1];
                        $('#select_dropdown').show();
                    }
                }
                if (result.result.role == "team_lead") {
                    if (result.result.list[0] == "none") {
                        $('#select_dropdown').hide();
                    }
                    var map_list = result.result.list;
                    self.mapping_list = map_list;
                    if (result.result.list[0] != "none"){
                        if ((result.result.list.length) == 2) {
                            var option = map_list[0];
                        }
                        else {
                        var option = map_list[1];
                        }
                        self.select_option = option.split(' - ')[1];
                        $('#select_dropdown').show();
                        $('#fileupload').hide();
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
                $('#videoPop').on('hidden.bs.modal', function () {
                $('video').get(0).pause();  
            }) 
                //debugger;
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
