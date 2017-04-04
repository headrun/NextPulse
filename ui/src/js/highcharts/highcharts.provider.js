;(function (angular, Highcharts) {
  "use strict";

  var highchartOptions = {

    "colors":[

      "#7cb5ec",

      "#434348",

      "#90ed7d",

      "#f7a35c",

      "#8085e9",

      "#f15c80",

      "#e4d354",

      "#8085e8",

      "#8d4653",

      "#91e8e1"

    ],

    "symbols":[

      "circle",

      "diamond",

      "square",

      "triangle",

      "triangle-down"

    ],

    "lang":{

      "loading":"Loading...",

      "months":[

        "January",

        "February",

        "March",

        "April",

        "May",

        "June",

        "July",

        "August",

        "September",

        "October",

        "November",

        "December"

      ],

      "shortMonths":[

        "Jan",

        "Feb",

        "Mar",

        "Apr",

        "May",

        "Jun",

        "Jul",

        "Aug",

        "Sep",

        "Oct",

        "Nov",

        "Dec"

      ],

      "weekdays":[

        "Sunday",

        "Monday",

        "Tuesday",

        "Wednesday",

        "Thursday",

        "Friday",

        "Saturday"

      ],

      "decimalPoint":".",

      "numericSymbols":[

        "k",

        "M",

        "G",

        "T",

        "P",

        "E"

      ],

      "thousandsSep":","

    },

    "chart":{

      "borderColor":"#4572A7",

      "borderRadius":0,

      "defaultSeriesType":"line",

      "ignoreHiddenSeries":true,

      "spacing":[

        10,

        10,

        15,

        10

      ],

      "backgroundColor":"#FFFFFF",

      "plotBorderColor":"#C0C0C0"
    },

    "title":{

      "text":"Chart title",

      "align":"center",

      "margin":15,

      "style":{

        "color":"#333333",

        "fontSize":"18px"

      }

    },

    "subtitle":{

      "text":"",

      "align":"center",

      "style":{

        "color":"#555555"

      }

    },

    "plotOptions":{

      "line":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":{

          "lineWidth":0,

          "radius":4,

          "lineColor":"#FFFFFF",

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000

      },

      "area":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":{

          "lineWidth":0,

          "radius":4,

          "lineColor":"#FFFFFF",

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000,

        "threshold":0

      },

      "spline":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":{

          "lineWidth":0,

          "radius":4,

          "lineColor":"#FFFFFF",

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000

      },

      "areaspline":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":{

          "lineWidth":0,

          "radius":4,

          "lineColor":"#FFFFFF",

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000,

        "threshold":0

      },

      "column":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":null,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null

        },

        "cropThreshold":50,

        "pointRange":null,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false,

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderRadius":0,

        "groupPadding":0.2,

        "pointPadding":0.1,

        "minPointLength":0,

        "tooltip":{

          "distance":6

        },

        "threshold":0

      },

      "bar":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":null,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null

        },

        "cropThreshold":50,

        "pointRange":null,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false,

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderRadius":0,

        "groupPadding":0.2,

        "pointPadding":0.1,

        "minPointLength":0,

        "tooltip":{

          "distance":6

        },

        "threshold":0

      },

      "scatter":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":0,

        "marker":{

          "lineWidth":0,

          "radius":4,

          "lineColor":"#FFFFFF",

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "tooltip":{

          "headerFormat":"<span style=\"color:{series.color}\">●</span> <span style=\"font-size: 10px;\"> {series.name}</span><br/>",

          "pointFormat":"x: <b>{point.x}</b><br/>y: <b>{point.y}</b><br/>"

        }

      },

      "pie":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":true,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom",

          "distance":30

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            },

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderWidth":1,

        "center":[

          null,

          null

        ],

        "clip":false,

        "colorByPoint":true,

        "ignoreHiddenPoint":true,

        "legendType":"point",

        "size":null,

        "showInLegend":false,

        "slicedOffset":10,

        "tooltip":{

          "followPointer":true

        }

      },

      "arearange":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":1,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null,

          "xLow":0,

          "xHigh":0,

          "yLow":0,

          "yHigh":0

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000,

        "threshold":null,

        "tooltip":{

          "pointFormat":"<span style=\"color:{series.color}\">●</span> {series.name}: <b>{point.low}</b> - <b>{point.high}</b><br/>"

        },

        "trackByArea":true

      },

      "areasplinerange":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":1,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null,

          "xLow":0,

          "xHigh":0,

          "yLow":0,

          "yHigh":0

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000,

        "threshold":null,

        "tooltip":{

          "pointFormat":"<span style=\"color:{series.color}\">●</span> {series.name}: <b>{point.low}</b> - <b>{point.high}</b><br/>"

        },

        "trackByArea":true

      },

      "columnrange":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":1,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null,

          "xLow":0,

          "xHigh":0,

          "yLow":0,

          "yHigh":0

        },

        "cropThreshold":300,

        "pointRange":null,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false,

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderRadius":0,

        "groupPadding":0.2,

        "pointPadding":0.1,

        "minPointLength":0,

        "tooltip":{

          "distance":6
        },

        "threshold":null,

        "trackByArea":true

      },

      "gauge":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":2,

        "marker":{

          "lineWidth":0,

          "radius":4,

          "lineColor":"#FFFFFF",

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":true,

          "x":0,

          "y":15,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px",

            "fontWeight":"bold"

          },

          "align":"center",

          "verticalAlign":"top",

          "defer":false,

          "borderWidth":1,

          "borderColor":"silver",

          "borderRadius":3,

          "crop":false,

          "zIndex":2

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":true,

        "turboThreshold":1000,

        "dial":{


        },

        "pivot":{


        },

        "tooltip":{

          "headerFormat":""

        },

        "showInLegend":false

      },

      "boxplot":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":1,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":null,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null

        },

        "cropThreshold":50,

        "pointRange":null,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false,

            "brightness":-0.3,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderRadius":0,

        "groupPadding":0.2,

        "pointPadding":0.1,

        "minPointLength":0,

        "tooltip":{

          "distance":6
        },

        "threshold":null,

        "fillColor":"#FFFFFF",

        "medianWidth":2,

        "whiskerLength":"50%",

        "whiskerWidth":2

      },

      "errorbar":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":1,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":null,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null

        },

        "cropThreshold":50,

        "pointRange":null,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":false,

            "brightness":-0.3,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderRadius":0,

        "groupPadding":0.2,

        "pointPadding":0.1,

        "minPointLength":0,

        "tooltip":{

          "distance":6,

          "pointFormat":"<span style=\"color:{series.color}\">●</span> {series.name}: <b>{point.low}</b> - <b>{point.high}</b><br/>"

        },

        "threshold":null,

        "fillColor":"#FFFFFF",

        "medianWidth":2,

        "whiskerLength":"50%",

        "whiskerWidth":null,

        "color":"#000000",

        "grouping":false,

        "linkedTo":":previous"

      },

      "waterfall":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":1,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":null,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":null,

          "verticalAlign":null

        },

        "cropThreshold":50,

        "pointRange":null,

        "states":{

          "hover":{

            "lineWidthPlus":0,

            "marker":{


            },

            "halo":false,

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#333",

        "borderRadius":0,

        "groupPadding":0.2,

        "pointPadding":0.1,

        "minPointLength":0,

        "tooltip":{

          "distance":6

        },

        "threshold":0,

        "lineColor":"#333",

        "dashStyle":"dot"

      },

      "bubble":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":{

          "duration":1000

        },

        "events":{


        },

        "lineWidth":0,

        "marker":{

          "lineWidth":1,

          "radius":4,

          "lineColor":null,

          "states":{

            "hover":{

              "enabled":true,

              "lineWidthPlus":1,

              "radiusPlus":2

            },

            "select":{

              "fillColor":"#FFFFFF",

              "lineColor":"#000000",

              "lineWidth":2

            }

          }

        },

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":false,

          "x":0,

          "y":0,

          "style":{

            "color":"white",

            "cursor":"default",

            "fontSize":"11px",

            "textShadow":"0px 0px 3px black"

          },

          "align":"center",

          "verticalAlign":"middle",

          "inside":true

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":5,

              "opacity":0.25

            }

          },

          "select":{

            "marker":{


            }

          }

        },

        "stickyTracking":false,

        "turboThreshold":0,

        "tooltip":{

          "headerFormat":"<span style=\"color:{series.color}\">●</span> <span style=\"font-size: 10px;\"> {series.name}</span><br/>",

          "pointFormat":"({point.x}, {point.y}), Size: {point.z}"

        },

        "minSize":8,

        "maxSize":"20%",

        "zThreshold":0

      },

      "funnel":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":false,

        "events":{


        },

        "lineWidth":2,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":true,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom",

          "distance":30,

          "connectorWidth":1,

          "connectorColor":"#606060"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            },

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderWidth":1,

        "center":[

          "50%",

          "50%"

        ],

        "clip":false,

        "colorByPoint":true,

        "ignoreHiddenPoint":true,

        "legendType":"point",

        "size":true,

        "showInLegend":false,

        "slicedOffset":10,

        "tooltip":{

          "followPointer":true

        },

        "width":"90%",

        "neckWidth":"30%",

        "height":"100%",

        "neckHeight":"25%",

        "reversed":false

      },

      "pyramid":{

        "allowPointSelect":false,

        "showCheckbox":false,

        "animation":false,

        "events":{


        },

        "lineWidth":2,

        "marker":null,

        "point":{

          "events":{


          }

        },

        "dataLabels":{

          "enabled":true,

          "x":0,

          "y":0,

          "style":{

            "color":"#606060",

            "cursor":"default",

            "fontSize":"11px"

          },

          "align":"center",

          "verticalAlign":"bottom",

          "distance":30,

          "connectorWidth":1,

          "connectorColor":"#606060"

        },

        "cropThreshold":300,

        "pointRange":0,

        "states":{

          "hover":{

            "lineWidthPlus":1,

            "marker":{


            },

            "halo":{

              "size":10,

              "opacity":0.25

            },

            "brightness":0.1,

            "shadow":false

          },

          "select":{

            "marker":{


            },

            "color":"#C0C0C0",

            "borderColor":"#000000",

            "shadow":false

          }

        },

        "stickyTracking":false,

        "turboThreshold":1000,

        "borderColor":"#FFFFFF",

        "borderWidth":1,

        "center":[

          "50%",

          "50%"

        ],

        "clip":false,

        "colorByPoint":true,

        "ignoreHiddenPoint":true,

        "legendType":"point",

        "size":true,

        "showInLegend":false,

        "slicedOffset":10,

        "tooltip":{

          "followPointer":true

        },

        "width":"90%",

        "neckWidth":"0%",

        "height":"100%",

        "neckHeight":"0%",

        "reversed":true

      }

    },

    "labels":{

      "style":{

        "position":"absolute",

        "color":"#3E576F"

      }

    },

    "legend":{

      "enabled":true,

      "align":"center",

      "layout":"horizontal",

      "borderColor":"#909090",

      "borderRadius":0,

      "navigation":{

        "activeColor":"#274b6d",

        "inactiveColor":"#CCC"

      },

      "shadow":false,

      "itemStyle":{

        "color":"#333333",

        "fontSize":"12px",

        "fontWeight":"bold",

        "cursor":"pointer"

      },

      "itemHoverStyle":{

        "color":"#000"

      },

      "itemHiddenStyle":{

        "color":"#CCC"

      },

      "itemCheckboxStyle":{

        "position":"absolute",

        "width":"13px",

        "height":"13px"

      },

      "symbolPadding":5,

      "verticalAlign":"bottom",

      "x":0,

      "y":0,

      "title":{

        "style":{

          "fontWeight":"bold"

        }

      }

    },

    "loading":{

      "labelStyle":{

        "fontWeight":"bold",

        "position":"relative",

        "top":"45%"

      },

      "style":{

        "position":"absolute",

        "backgroundColor":"white",

        "opacity":0.5,

        "textAlign":"center"

      }

    },

    "tooltip":{

      "enabled":true,

      "animation":true,

      "backgroundColor":"rgba(249, 249, 249, .85)",

      "borderWidth":1,

      "borderRadius":3,

      "dateTimeLabelFormats":{

        "millisecond":"%A, %b %e, %H:%M:%S.%L",

        "second":"%A, %b %e, %H:%M:%S",

        "minute":"%A, %b %e, %H:%M",

        "hour":"%A, %b %e, %H:%M",

        "day":"%A, %b %e, %Y",

        "week":"Week from %A, %b %e, %Y",

        "month":"%B %Y",

        "year":"%Y"

      },

      "headerFormat":"<span style=\"font-size: 10px\">{point.key}</span><br/>",

      "pointFormat":"<span style=\"color:{series.color}\">●</span> {series.name}: <b>{point.y}</b><br/>",

      "shadow":true,

      "snap":10,

      "style":{

        "color":"#333333",

        "cursor":"default",

        "fontSize":"12px",

        "padding":"8px",

        "whiteSpace":"nowrap"

      }

    },

    "credits":{

      "enabled":true,

      "text":"Highcharts.com",

      "href":"http://www.highcharts.com",

      "position":{

        "align":"right",

        "x":-10,

        "verticalAlign":"bottom",

        "y":-5

      },

      "style":{

        "cursor":"pointer",

        "color":"#909090",

        "fontSize":"9px"

      }

    }
  };

  angular.module("highcharts")
         .provider("highcharts", function () {

           this.options = highchartOptions;

           this.setOptions = function (options) {

             options = options || {};

             angular.extend(this.options, options);
           };
         });

}(window.angular, window.Highcharts));
