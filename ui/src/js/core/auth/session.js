;(function (angular) {
  "use strict";

  angular.module("auth").service("Session", function () {

    var that = this;

    function resetSession () {

      angular.extend(that, {

        "userId"  : null,
        "userName": null,
        "email"   : null,
        "roles"   : []
      });
    }

    resetSession();

    this.get = function () {

      return {

        "userId"  : this.userId,
        "userName": this.userName,
        "email"   : this.email,
        "roles"   : this.roles
      };
    };

    this.set = function (data) {

      this.userId   = data.userId;
      this.userName = data.userName;
      this.email    = data.email;
      this.roles    = data.roles;
    };

    this.unset = resetSession;
  });

}(window.angular));
