;(function (angular) {
  "use strict";

  angular.module("review")
         .component("review", {

           "templateUrl": "/js/review/review.html",
           "controller": ['$http','$scope','$rootScope',

           function ($http,$scope,$rootScope) {

             var self = this;

             self.submit_type = '';

             self.review_types_all = ['select', 'Weekly', 'Monthly', 'Quarterly', 'Adhoc'];

             self.edit_review = {
                    'reviewname': '', 'reviewdate': '', 'reviewtime': '', 'bridge': '', 'venue': '', 'review_type': '', 
                    'reviewagenda': '', 'participants': '', 'rev_str': 'Edit Review'
                    };

             self.add_review = {
                    'reviewname': '', 'reviewdate': '', 'reviewtime': '', 'bridge': '', 'venue': '', 'review_type': self.review_types_all[0], 
                    'reviewagenda': '', 'participants': '', 'rev_str': 'Add Review'
                    };

             self.rev_id = '';

             self.email_data = 'api/get_related_user/';

             self.no_data = true;

             self.part_disable = true;

             self.is_lead = true;

             $http.get(self.email_data).then(function(result){
		if (result.data.result == 'User is not TeamLead'){
		self.stat = false;
		}else{
                self.stat = true;
                var names_list = result.data.result.name_list;
                var ids_list = result.data.result.id_list;
                self.mail_options = names_list;
                var some = {}
                names_list.map(function(e, i){
                    some[e] = ids_list[i]
                });
                self.map_list_item = some;
		}
             });

            /* self.mail_options = [ "Shanmugasundaram v", "Monica M", "Abhijith A", "Sasikumar G", "Ranjithkumar M", "Shailesh dube", 
                                   "Atul shinghal", "Navin Ramachandran", "Goutam Dan", "rajesh r", "Damodaran Selvaraj", "Balasubramanian A", 
                                   "Anuradha G", "Arun L", "Sunilbabu S", "Hariharan N", "Anandram J", "Venkatesh D" ];*/
       	    // self.mail_options = [ "sankar K", "poornima mitta", "Kannan sundar", "Sriram ."];

             self.review_url = 'api/get_top_reviews/';

             $('#ong-meet').hide();

             $http.get(self.review_url).then(function(result){


		 if (result.data.result.is_team_lead == false){
                    $('#fileuploader').hide();
			        $('.add-review').hide();
                    self.is_lead=false;
		  }

		 if (Object.keys(result.data.result.all_data).length != 0) {
                 //self.mail_options = [ "Shanmugasundaram v", "Monica M", "Abhijith A", "Sasikumar G", "Ranjithkumar M", "Shailesh dube"];

                 self.all_reviews = result.data.result.all_data;
		         self.no_data = true;
                 self.part_disable = true;
                 $('.loading').removeClass('show').addClass('hide');
                 self.rev_id = self.all_reviews[Object.keys(self.all_reviews)[0]][0].id;
                 self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                 /*if (result.data.result[Object.keys(result.data.result)[0]][0].is_team_lead == false){
                    $('#fileuploader').hide();
                    $('#add-revi').hide();
		    self.is_lead=false;
                 }*/
                 //$('.loading').removeClass('show').addClass('hide');
                 return self.rev_id;

		}
		else {
		 $('.loading').removeClass('show').addClass('hide');
		 self.no_data = false;
		 self.part_disable = false;
         if (self.is_lead){
            $('.fa-pencil-square-o').hide();
            $('.fa-trash').hide();
            swal('No reviews available! Click on plus button to create a new reveiw');
            $('.fa-plus-circle').show();
        }
        else {
            $('.fa-plus-circle').hide();
            swal('No Reviews Available!');
            }
		}
             });

             self.get_review = function(review){

                 $('.loading').removeClass('hide').addClass('show');
                 self.rev_id = review.id;
                 var sel_rev_id = self.rev_id;

             if (self.is_lead && !$('#check-past').is(':checked')) {
                     self.no_data = true;
                     setTimeout(function(){
                     $("#fileuploader").uploadFile({
                        url:"/api/upload_review_doc/",
                        dragDrop:false,
                        fileName:"myfile",
                        formData:{"review_id": self.rev_id },
                        onSuccess:function(files,data,xhr,pd,sel_rev_id){

                            if (data.result == "Improper File name") {
                                swal('File name in not proper!');
                                $('.ajax-file-upload-statusbar').hide();

                            }
                            else if (data.result == "File size is bigger than 10 MB"){
                                swal("File size is bigger than 10 MB!");
                                $('.ajax-file-upload-statusbar').hide();

                                }
                            else{
                                $('.ajax-file-upload-statusbar').hide();
                                $('.loading').removeClass('hide').addClass('show');
                                self.get_data_url = 'api/get_review_details/?review_id='+data.result;

                                $http.get(self.get_data_url).then(function(result){
                                    self.all_review_data = result.data.result.rev_files;
                                    self.no_data = true;
                                    self.part_disable = true;
                                    $('.loading').removeClass('show').addClass('hide');
                                });
                            }
                        }
                    });
                    }, 1000);
             }else{
                $("#fileuploader").html('');    
             }

                 self.get_data_url = 'api/get_review_details/?review_id='+self.rev_id;

                 $http.get(self.get_data_url).then(function(result){

                    self.edit_review['participants'] = [];
		            self.no_data = true;
        		    self.part_disable = true;
                    var all_selec = result.data.result.members;
                    for (var i=0; i<all_selec.length; i++){
                        self.edit_review['participants'].push(all_selec[i]['name']);
                    }
                    self.edit_review['reviewname'] = result.data.result.name;
                    //self.edit_review['reviewtime'] = result.data.result.time;
                    var fi = result.data.result.jq_date;
                    self.edit_review['reviewtime'] = new Date(fi[0], fi[1]-1, fi[2], fi[3], fi[4], fi[5]);
                    self.rev_time = result.data.result.time;
                    self.rev_date = result.data.result.date;
                    self.edit_review['reviewdate'] = new Date(fi[0], fi[1]-1, fi[2]);
                    self.rev_day = result.data.result.day;
                    self.rev_tl = result.data.result.tl;
                    self.edit_review['reviewagenda'] = result.data.result.agenda;
                    self.edit_review['bridge'] = result.data.result.bridge;
                    self.edit_review['venue'] = result.data.result.venue;
                    self.edit_review['review_type'] = result.data.result.review_type;
                    self.all_review_data = result.data.result.rev_files;
                    self.is_when = result.data.result.remained;
                    self.membs = result.data.result.members;

                    self.review = self.edit_review;
                    $('.loading').removeClass('show').addClass('hide');

                 });
             }

            self.get_all_reviews = function() {
                self.past_reviews = false;
                if ($('#check-past').is(':checked')) {
                    self.all_review_url = 'api/get_top_reviews/?timeline=past';
                    $('#past-meet').hide();
                    $('#ong-meet').show();
                    self.past_reviews = true;
                    //$('.fa-pencil-square-o').hide();
                }
                else {
                    self.all_review_url = 'api/get_top_reviews/?timeline=oncoming';
                    $('#ong-meet').hide();
                    $('#past-meet').show();
                    self.past_reviews = false;
                    //$('.fa-pencil-square-o').show();
                }
                $http.get(self.all_review_url).then(function(result){

                 self.all_reviews = result.data.result.all_data;
                 $('.loading').removeClass('show').addClass('hide');
		 if (Object.keys(self.all_reviews).length != 0){
                 self.rev_id = self.all_reviews[Object.keys(self.all_reviews)[0]][0].id;
                 self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                 if (self.past_reviews) {
                     $('.fa-trash').show();
                     $('.fa-plus-circle').hide();
                     $('.fa-pencil-square-o').hide();
                 }
                 else {
                    $('.fa-plus-circle').show();    
                    $('.fa-pencil-square-o').show();
                    $('.fa-trash').show();
                 }
                 /*if (result.data.result[Object.keys(result.data.result)[0]][0].is_team_lead == false){
                    $('#fileuploader').hide();
                    $('#add-revi').hide();
                 }*/
                 //$('.loading').removeClass('show').addClass('hide');
                 return self.rev_id;
		     }
		 else { 
                 if (self.past_reviews) {
                     $('.fa-trash').hide();
                     $('.fa-plus-circle').hide();
                     $('.fa-pencil-square-o').hide();
                 }   
                 else {
                    $('.fa-plus-circle').show();    
                    $('.fa-pencil-square-o').hide();
                    $('.fa-trash').hide();
                 } 
             self.edit_review = { 
                    'reviewname': '', 'reviewdate': '', 'reviewtime': '', 'bridge': '', 'venue': '', 'review_type': '', 
                    'reviewagenda': '', 'participants': '', 'rev_str': 'Edit Review'
                    };
			self.rev_time = '';
			self.rev_date = '';
			self.rev_day = '';
			self.rev_tl = '';
			self.all_review_data = '';
			self.is_when = '';
			self.membs = ''; 
			self.no_data = false;

			self.part_disable = false;
         if (self.is_lead){
//            swal('No Reviews Available! Click on plus button to create a new reveiw');
            swal('No Reviews Available!');
        }   
        else {
            swal('No Reviews Available!');
            }   

		      }
               });
            };

            self.download_file = function(file) {
                var file_id = file.name.split('#')[1];
                self.download_url = '/api/download_attachments/?doc_id='+file_id;
                $http.get(self.download_url).then(function(result){
                });
            }

            self.get_maildata = function(type_handle){
               
              if (type_handle == 'create') {
                //$('.input-clear').val('');
                self.review = self.add_review;
                self.submit_type = 0;
                self.track_id = 0;
                self.add_review = { 
                    'reviewname': '', 'reviewdate': '', 'reviewtime': '', 'bridge': '', 'venue': '', 'review_type': self.review_types_all[0], 
                    'reviewagenda': '', 'participants': '', 'rev_str': 'Add Review'
                    };
              }
              else {
                self.review = self.edit_review;
                self.appendValues(self.edit_review);
                self.review.reviewdate = self.review.reviewtime;
                self.submit_type = 1;
                self.track_id = self.rev_id;
              }
            };

            self.appendValues = function(data_array){
                
                $('.modal').find('input[name="reviewname"]').val(data_array.reviewname);
                $('.modal').find('input[name="bridge"]').val(data_array.bridge);
                $('.modal').find('input[name="venue"]').val(data_array.venue);
                $('.modal').find('input[name="revDate"]').val(data_array.reviewtime);
                $('.modal').find('textarea[name="reviewagenda"]').val(data_array.reviewagenda);
            }


             self.submit = function(review) {
                var selected_date = moment(review.reviewtime);
                var today = moment(new Date());
                var past_days = today.set({hour:0,minute:0,second:0,millisecond:0});
                if (selected_date.format('YYYY-MM-DD') == "Invalid date"){
                    //swal('Invalid date entered!');
                    swal({
                      title: "Invalid date entered!",
                      text: "", 
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: "#DD6B55",
                      confirmButtonText: "Okay",
                      cancelButtonText: "", 
                      closeOnConfirm: true,
                      closeOnCancel: false
                    },  
                    function(isConfirm){
                      if (isConfirm) {
                        $('#myModal').modal('show');
                      }   
                    }); 
                }else if(today.format('YYYY-MM-DD') == selected_date.format('YYYY-MM-DD') && selected_date.diff(moment(), 'minutes') < 0){
                    swal('Creating reviews in past time is restricted!');
                }else if(today.format('YYYY-MM-DD') > selected_date.format('YYYY-MM-DD')){
                    if (selected_date.diff(past_days) < 0){
                        swal('Creating reviews in past date is restricted!');
                    }
                }
                else {
        if (review.reviewname && review.reviewtime && review.reviewagenda && review.review_type != 'select'){
            self.uids_list = []
            for (var i=0; i<review.participants.length; i++) {
                self.uids_list.push(self.map_list_item[review.participants[i]]);
                }
            $('.input-clear').val('');
            $('.loading').removeClass('hide').addClass('show');
            self.create_rev_url = 'api/create_reviews/';
            var data = {}
            //review.reviewtime = review.reviewdate;    
            angular.forEach(review, function(key, value) {
                if (key) {
                    data[value] = key.toString()
                }else { 
                    data[value] = ''
                }
                });
            data['id'] = self.submit_type;
            data['track_id'] = self.track_id;
            var main_data = $.param({ json: JSON.stringify(data) });
            $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
            $http.post(self.create_rev_url, (main_data)).then(function(result){
		        if (result.data == "Improper File name"){
			        swal("Improper review name!");
                    /*swal({
                      title: "Improper review name!",
                      text: "", 
                      type: "error",
                      showCancelButton: false,
                      confirmButtonColor: "#DD6B55",
                      confirmButtonText: "Okay",
                      cancelButtonText: "", 
                      closeOnConfirm: true,
                      closeOnCancel: false
                    },  
                    function(isConfirm){
                      if (isConfirm) {
                        $('#myModal').modal('show');
                      }   
                    });*/ 
		            }
                return result.data.result;
                }).then(function(callback){

                   var data2 = {'review_id': callback, 'uids': self.uids_list};
                   var data_to_send = $.param({ json: JSON.stringify(data2)});
                   $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
                   $http.post('api/saving_members/', data_to_send).then(function(result){
                    }).then(function() {

                   $http.get(self.review_url).then(function(result){
                      if (result.data.result.is_team_lead == false){
                        self.is_lead = false;
                        
                      } 
                     self.all_reviews = result.data.result.all_data;
                     $('.fa-pencil-square-o').show();
                     $('.fa-trash').show();
		     if ((Object.keys(result.data.result.all_data).length) != 0){
                    if(self.is_lead){
                        self.no_data = true;
                    }
                    setTimeout(function(){
                        self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                        }, 600)
//                         self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
		     }
                     $('.loading').removeClass('show').addClass('hide');

                   })

                 });
                });
		}
        else {
            var message = '';
            if (review.reviewname == ""){
                message += 'Add review name.'
                }
            if (review.reviewagenda == ""){
                message += ' Add review agenda.'
                }
            if (review.review_type == 'select'){
                message += ' Select review type.'
                }
            swal({
              title: "All required fields are not filled!",
              text: message, 
              type: "error",
              showCancelButton: false,
              confirmButtonColor: "#DD6B55",
              confirmButtonText: "Okay",
              cancelButtonText: "", 
              closeOnConfirm: true,
              closeOnCancel: false
            },  
            function(isConfirm){
              if (isConfirm) {
                $('#myModal').modal('show');
              }   
            }); 

       }
    }
                }

             self.remove_file = function(file_id) {

                swal({
                  title: "Are you sure?",
                  text: "You will not be able to recover this attachment file!",
                  type: "warning",
                  showCancelButton: true,
                  confirmButtonColor: "#DD6B55",
                  confirmButtonText: "Yes, delete it!",
                  cancelButtonText: "No, cancel pls!",
                  closeOnConfirm: false,
                  closeOnCancel: false
                },

                function(isConfirm){
                    if (isConfirm) {
                 $('.loading').removeClass('hide').addClass('show');

                 self.remove_file_url = 'api/remove_attachment/?file_id='+file_id+'&term_type=attachment';

                 $http.get(self.remove_file_url).then(function(result){

                    self.get_data_url = 'api/get_review_details/?review_id='+result.data.result.rev_id;

                 $http.get(self.get_data_url).then(function(result){

                    self.all_review_data = result.data.result.rev_files;
		    self.no_data = true;
		    self.part_disable = true;
                    $('.loading').removeClass('show').addClass('hide');
                 });

                 });
                    swal("Deleted!", "Your attachment file has been deleted.", "success");
                }
                else {
                    swal("Cancelled", "Your attachment file is safe :)", "error");
                 }
                });
             }

         self.del_review = function() {

            swal({
              title: "Ar you sure?",
              text: "You will not be able to recover this review!",
              type: "warning",
              showCancelButton: true,
              confirmButtonColor: "#DD6B55",
              confirmButtonText: "Yes, delete it!",
              cancelButtonText: "No, cancel pls!",
              closeOnConfirm: false,
              closeOnCancel: false
            },
            function(isConfirm){
              if (isConfirm) {
                    $('.loading').removeClass('hide').addClass('show');

                    self.remove_review_url = 'api/remove_attachment/?file_id='+self.rev_id+'&term_type=review';

                    $http.get(self.remove_review_url).then(function(result){}).then(function (result){
                      $http.get(self.review_url).then(function(result){
                        if (result.data.result.is_team_lead == false){
                            self.is_lead=false;
                        } 
            if (Object.keys(result.data.result.all_data).length != 0) {
		        self.all_reviews = result.data.result.all_data;
                self.rev_id = self.all_reviews[Object.keys(self.all_reviews)[0]][0].id;
                self.get_review(self.all_reviews[Object.keys(self.all_reviews)[0]][0]);
                //return self.rev_id;
                $('.loading').removeClass('show').addClass('hide');
                if (self.is_lead){
                    $('.fa-plus-circle').show();
                    $('.fa-pencil-square-o').show();
                    $('.fa-trash').show();
                    }
                return self.rev_id;
			}else{
                if (self.is_lead){
                     $('.fa-plus-circle').show();
                }
                $('.fa-pencil-square-o').hide();
                $('.fa-trash').hide();
			self.all_reviews = result.data.result.all_data;
                   self.edit_review = {
                    'reviewname': '', 'reviewdate': '', 'reviewtime': '', 'bridge': '', 'venue': '', 'review_type': '',
                    'reviewagenda': '', 'participants': '', 'rev_str': 'Edit Review'
                    };  
                        self.rev_time = '';
                        self.rev_date = '';
                        self.rev_day = '';
                        self.rev_tl = '';
                        self.all_review_data = '';
                        self.is_when = '';
                        self.membs = '';
                        self.no_data = false;

                        self.part_disable = false;

			$('.loading').removeClass('show').addClass('hide');
            swal('No Reviews Available! Click on plus button to create a new reveiw');
			}
                      });
                    });
                swal("Deleted!", "Your Review has been deleted.", "success");

               $('#check-past').attr('checked', false);
               $('#ong-meet').hide();
               $('#past-meet').show();
              } else {
                swal("Cancelled", "Your Review is safe :)", "error");
              }
            });
         }

         $(window).on('popstate', function() {
            swal.close();
         });

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
