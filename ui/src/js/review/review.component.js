;(function (angular) {
  "use strict";

  angular.module("review")
         .component("review", {

           "templateUrl": "/js/review/review.html",
           "controller": ['$http','$scope','$rootScope',

           function ($http,$scope,$rootScope) {

             var self = this;

             self.hideLoading();

             self.review_url = 'api/get_top_reviews/'

             $http.get(self.review_url).then(function(result){

                 self.all_reviews = result.data.result.all_data;
             });

             self.get_review = function(review){

                 self.rev_id = review.id;

                 self.get_data_url = 'api/get_review_details/?review_id='+self.rev_id;

                 $http.get(self.get_data_url).then(function(result){

                     self.rev_date = result.data.result.date;

                     self.rev_name = result.data.result.name;

                     self.rev_time = result.data.result.time;

                     self.rev_tl = result.data.result.tl;
                 });
             }

         }],

            "bindings": {

              "hideLoading": "&",
              "showLoading": "&"
            }
         });

}(window.angular));
