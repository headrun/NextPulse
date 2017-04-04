;(function (angular) {
  "use strict";

  var _ = window._; //underscore.js

  var YEARS = ["2016", "2015", "2014"];

  var yearValues = [];

  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May",
                "Jun", "Jul", "Aug", "Sep", "Oct",
                "Nov", "Dec"];

  var QUARTERS = ["Q1", "Q2", "Q3", "Q4"];

  angular.forEach(YEARS, function (year) {

    yearValues.push([year]);
  });

  var monthValues = [];

  angular.forEach(MONTHS, function (month, index) {

    monthValues.push([index + 1 + "", month]);
  });

  var quarterValues = [];

  angular.forEach(QUARTERS, function (quarter, index) {

    quarterValues.push([index + 1 + "", quarter]);
  });

  function getMonthByIndex (index) {

    return MONTHS[window.parseInt(index) - 1];
  }

  function getQuarterByIndex (index) {

    return QUARTERS[window.parseInt(index) - 1];
  }

  function sortKeys (data, keysOrder, dec) {

    /*
     * Sorts dictionary keys in an order, by default string sort,
     * or if keyOrder is given, keys will be sorted in that order
     */

    var sortedData = [];

    if (keysOrder) {

      angular.forEach(keysOrder, function (key) {

        sortedData.push([key, data[key]]);
      });
    } else {

      data = _.pairs(data);

      sortedData = _.sortBy(data, function (item) { return item[0]; });
    }

    if (dec) {

      sortedData.reverse();
    }

    return sortedData;
  }

  function updateFilters(allFilters, selectedFilters) {

    angular.forEach(allFilters, function (value, filter) {

      if (value.type === "dropdown") {

        value.selected = selectedFilters[filter] ||
                         value.selected ||
                         value.values[0] && value.values[0][0];
      } else if(value.type === "checkbox") {

        value.selected = !!selectedFilters[filter];
      }
    });
  }

  function getAPIParams(allFilterNames, selectedFilters) {

    var params = {};

    angular.forEach(allFilterNames, function (filterName) {

      var filterVal = selectedFilters[filterName];

      if (angular.isDefined(filterVal)) {

        params[filterName] = filterVal;
      }
    });

    return params;
  }

  function makeListOfLists (list) {

    var retVal = [];

    for (var index in list) {

      var item = list[index];

      if (item) {

        retVal.push([item]);
      }
    }

    return retVal;
  }

  angular.module("utils", [])
         .service("utils", function () {

           this.yearValues = yearValues;
           this.monthValues = monthValues;
           this.quarterValues = quarterValues;
           this.sortKeys = sortKeys;
           this.updateFilters = updateFilters;
           this.getAPIParams = getAPIParams;
           this.getMonthByIndex = getMonthByIndex;
           this.getQuarterByIndex = getQuarterByIndex;
           this.makeListOfLists = makeListOfLists;
         });
}(window.angular));
