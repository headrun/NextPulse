;(function (angular) {
  "use strict";

  angular.module("review")
         .component("review", {

           "templateUrl": "/js/review/review.html",
           "controller": ['$http','$scope','$rootScope',

           function ($http,$scope,$rootScope) {

             var self = this;

             self.hideLoading();

             self.rev_id = '';

             self.email_data = 'api/get_related_user/'

             /*self.mail_options = [];

                 $http.get(self.email_data).then(function(result){

                     self.mail_options.push(result.data.result.name_list);
                 });*/

             self.mail_options = ["Asifa", "Abhishek", "Yeswanth", "Rishi", "Kannan", "Poornima", "Sankar"]

             self.review_url = 'api/get_top_reviews/'

             $http.get(self.review_url).then(function(result){

                 self.all_reviews = result.data.result;
                 self.rev_id = self.all_reviews[Object.keys(self.all_reviews)[0]][0].id;
                 self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                 return self.rev_id;
             }).then(function(callback){

             /*$("#fileuploader").uploadFile({
                url:"/api/create_reviews/",
                dragDrop:false,
                fileName:"myfile",
                formData:{"review_id": callback }
             });*/

             });

             self.get_review = function(review){

                 self.rev_id = review.id;
                 var sel_rev_id = self.rev_id;

             $("#fileuploader").uploadFile({
                url:"/api/upload_review_doc/",
                dragDrop:false,
                fileName:"myfile",
                formData:{"review_id": self.rev_id },
                onSuccess:function(files,data,xhr,pd,sel_rev_id){
                    $('.ajax-file-upload-statusbar').hide();
                    self.get_data_url = 'api/get_review_details/?review_id='+data.result;

                 $http.get(self.get_data_url).then(function(result){

                    self.all_review_data = result.data.result.rev_files;
                 });
                }
             });

                 self.get_data_url = 'api/get_review_details/?review_id='+self.rev_id;

                 $http.get(self.get_data_url).then(function(result){

                    self.rev_text = result.data.result.name;
                    self.rev_time = result.data.result.time;
                    self.rev_date = result.data.result.date;
                    self.rev_day = result.data.result.day;
                    self.rev_tl = result.data.result.tl;
                    self.rev_agenda = result.data.result.agenda;
                    self.all_review_data = result.data.result.rev_files;

                 });
             }

             self.submit = function(review) {

                 self.create_rev_url = 'api/create_reviews/';
                 var data = {}
                 angular.forEach(review, function(key, value) {
                     data[value] = key.toString()
                 })

                 var main_data = $.param({ json: JSON.stringify(data) });
                 $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                 $http.post(self.create_rev_url, main_data).then(function(result){
                 }).then(function(callback){
             $http.get(self.review_url).then(function(result){

                 self.all_reviews = result.data.result;
                 self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
             });
                 });
             }

             self.remove_file = function(file_id) {

                 self.remove_file_url = 'api/remove_attachment/?file_id='+file_id+'&term_type=attachment';

                 $http.get(self.remove_file_url).then(function(result){
                    
                    self.get_data_url = 'api/get_review_details/?review_id='+result.data.result;

                 $http.get(self.get_data_url).then(function(result){

                    self.all_review_data = result.data.result.rev_files;
                 });

                 });

             }

         }],

            "bindings": {

              "hideLoading": "&",
              "showLoading": "&"
            }
         })
         .filter('getdate', function(){

             return function(input, day_data){

                 var date_dd = input.split('_')[0];
                 var day = input.split('_')[2];
                 var month = input.split('_')[1];

                 if (day_data == 'had') {
                    date_dd = month;
                 }
                 if (day_data == true) {
                    date_dd = day.slice(0,3) 
                 }
               return date_dd
             };
         })
         .filter('getfile', function() {

             return function(input, file_id){

                 var file_name = input.split('#')[0];
                 var fileid = input.split('#')[1];
                 if (file_id) {
                     file_name = fileid
                 }
              return file_name
             };
         });

}(window.angular));
