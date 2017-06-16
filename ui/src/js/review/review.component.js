;(function (angular) {
  "use strict";

  angular.module("review")
         .component("review", {

           "templateUrl": "/js/review/review.html",
           "controller": ['$http','$scope','$rootScope',

           function ($http,$scope,$rootScope) {

             var self = this;

             self.rev_id = '';

             self.email_data = 'api/get_related_user/';

             self.mail_options = [ "Shanmugasundaram v", "Monica M", "Abhijith A", "Sasikumar G", "Ranjithkumar M", "Shailesh dube", 
                                   "Atul shinghal", "Navin Ramachandran", "Goutam Dan", "rajesh r", "Damodaran Selvaraj", "Balasubramanian A", 
                                   "Anuradha G", "Arun L", "Sunilbabu S", "Hariharan N", "Anandram J", "Venkatesh D" ];

             self.review_url = 'api/get_top_reviews/';

             $http.get(self.review_url).then(function(result){

                 self.all_reviews = result.data.result;
                 self.rev_id = self.all_reviews[Object.keys(self.all_reviews)[0]][0].id;
                 self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                 if (result.data.result[Object.keys(result.data.result)[0]][0].is_team_lead == false){
                    $('#fileuploader').hide();
                    $('#add-revi').hide();
                 }
                 $('.loading').removeClass('show').addClass('hide');
                 return self.rev_id;
             });

             self.get_review = function(review){

                 $('.loading').removeClass('hide').addClass('show');
                 self.rev_id = review.id;
                 var sel_rev_id = self.rev_id;

             $("#fileuploader").uploadFile({
                url:"/api/upload_review_doc/",
                dragDrop:false,
                fileName:"myfile",
                formData:{"review_id": self.rev_id },
                onSuccess:function(files,data,xhr,pd,sel_rev_id){
                    $('.ajax-file-upload-statusbar').hide();
                    $('.loading').removeClass('hide').addClass('show');
                    self.get_data_url = 'api/get_review_details/?review_id='+data.result;

                 $http.get(self.get_data_url).then(function(result){

                    self.all_review_data = result.data.result.rev_files;
                    $('.loading').removeClass('show').addClass('hide');
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
                    self.is_when = result.data.result.remained;
                    $('.loading').removeClass('show').addClass('hide');

                 });
             }

             self.submit = function(review) {
                 self.map_list_item = { "Shanmugasundaram v": 15, "Monica M": 18, "Abhijith A": 19, "Sasikumar G": 101, "Ranjithkumar M": 107, 
                                        "Shailesh dube": 2, "Atul shinghal": 116,  "Navin Ramachandran": 123, "Goutam Dan": 127, "rajesh r": 25, 
                                        "Damodaran Selvaraj": 52, "Balasubramanian A": 59, "Anuradha G": 60, "Arun L": 61, "Sunilbabu S": 62, 
                                        "Hariharan N": 63, "Anandram J": 90, "Venkatesh D":91 }
                 self.uids_list = []
                 for (var i=0; i<review.selection.length; i++) {
                    self.uids_list.push(self.map_list_item[review.selection[i]]);
                 }
                 $('.input-clear').val('');
                 //$('.input-clear')
                 $('.loading').removeClass('hide').addClass('show');
                 self.create_rev_url = 'api/create_reviews/';
                 var data = {}
                 angular.forEach(review, function(key, value) {
                     data[value] = key.toString()
                 })

                 var main_data = $.param({ json: JSON.stringify(data) });
                 $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                 $http.post(self.create_rev_url, main_data).then(function(result){

                    return result.data.result;
                 }).then(function(callback){

                   $http.get(self.review_url).then(function(result){

                     var data2 = {'review_id': callback, 'uids': self.uids_list}
                     var data_to_send = $.param({ json: JSON.stringify(data2)})
                     $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                     $http.post('api/saving_members/', data_to_send).then(function(result){
                     });
                     self.all_reviews = result.data.result;
                     self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                     $('.loading').removeClass('show').addClass('hide');
                   });
                 });
             }

             self.remove_file = function(file_id) {

                 $('.loading').removeClass('hide').addClass('show');

                 self.remove_file_url = 'api/remove_attachment/?file_id='+file_id+'&term_type=attachment';

                 $http.get(self.remove_file_url).then(function(result){

                    self.get_data_url = 'api/get_review_details/?review_id='+result.data.result;


                 $http.get(self.get_data_url).then(function(result){

                    self.all_review_data = result.data.result.rev_files;
                    $('.loading').removeClass('show').addClass('hide');
                 });

                 });

             }

         self.del_review = function() {
            console.log(self.rev_id);

            self.remove_review_url = 'api/remove_attachment/?review_id='+self.rev_id;

            $http.get(self.remove_review_url).then(function(result){
            
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
