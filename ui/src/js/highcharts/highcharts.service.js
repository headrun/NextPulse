;(function (angular) {
  "use strict";

  var Highcharts = window.Highcharts;

  angular.module("highcharts")
         .service("highcharts", function () {

           var that = this;

           console.log(this);

           this.render = function (element, options) {

             options = options || {};

             return new Highcharts(angular.extend(

                      {}, this.options, options, {"chart": {"renderTo": element}}
                    ));
           };
         });
}(window.angular));
