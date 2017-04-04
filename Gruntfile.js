module.exports = function (grunt) {

  var BASE_DIR = process.cwd() + "/ui/src",
      JS_DIR   = BASE_DIR + "/js",
      LESS_DIR = BASE_DIR + "/less";

  require("matchdep").filterDev("grunt-contrib-*").forEach(grunt.loadNpmTasks);

  function prepareConfig () {

    var tasks = {};

    tasks.jshint = {

      "options": {

        "jshintrc": true
      },
      "all": [JS_DIR + "/**/*.js"]
    };

    tasks.less = {

      "all": {

        options: {
          plugins: [
            new (require('less-plugin-clean-css'))({})
          ]
        },
        src : LESS_DIR + "/app.less",
        dest: BASE_DIR + "/app.css"
      }
    };

    return tasks;
  }

  grunt.initConfig(prepareConfig());

  grunt.registerTask("default", ["jshint", "less"]);
};
