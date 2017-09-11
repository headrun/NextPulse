;(function($){
    "use strict";

    var _ = window._;//underscore js

    var _get_popover_tmpl;

    window.buzz_data = window.buzz_data || {};

    var keydown_whitelist = [38, 37, 40, 39];

    var blacklist_keys = [9, 13, 27, 220, 16, 17, 91, 218, 0, 38, 37, 40, 39, 45, 36, 33, 34, 35, 46, 12, 112, 113, 114, 115, 116, 117, 118];

    var setCaret = function(el, index) {


        if(!el) return;

        var range = document.createRange();
        var sel = window.getSelection();

        index = index || $(el)
            .text()
            .length;

        if (el.childNodes.length > 0) {

            range.setStart(el.childNodes[0], index);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
        }
        $(el).focus().trigger("click");

        return el;
    }

    buzz_data.utils = {"show_message": function(msg) {window.alert(msg);}};

    // The Annotation constructor
    var Annotation = buzz_data.Annotation = function(graph_name, $graph, chart, point, data){
        //if ($graph[0].id == 'highcharts-4') { debugger; };

        //$graph = '#'+$graph[0].id;


        graph_name = graph_name || "overview";

        var that = this;

        var new_annotation = !data;

        that.new_annotation = new_annotation;

        if(new_annotation){

            that.annot_saved = false;

            if (graph_name.indexOf("Week") > 0) {

                if (graph_name.indexOf("bar") > 0) {

                    data = {"id": _.uniqueId("annotation-week-bar-")};
                }

                else {

                    data = {"id": _.uniqueId("annotation-week-")};
                }
            }
            else {

                if (graph_name.indexOf("bar") > 0) {

                    data = {"id": _.uniqueId("annotation-bar-")};
                }

                else {

                    var key_used = point.series.name + point.category + graph_name

                    key_used = key_used.split(' ').join('');

                    if (key_used.indexOf("&") > 0) {

                        key_used = key_used.replace('&','and');
                    }

                    key_used = 'annotation-' + key_used;

                    data = {"id": _.uniqueId("annotation-")};
                }
            }

            data["text"] = "";
            data["epoch"] = point.category;
            data["graph_name"] = graph_name;
            data["series_name"] = point.series.name;
            data["widget_id"] = graph_name.split('<##>')[0];
            data["project_live"] = point.project_live;
            data["center_live"] = point.center_live;
        }

        if((point.barX) & (point.pointWidth < 55)){

            var instance = chart.renderer.image('/img/marker.png',
                                                point.barX + point.plotX - 10,
                                                point.plotY - chart.plotTop -30,
                                                20,
                                                24)
                                         .attr({
                                                "zIndex": 10,
                                                "class": "annotation-marker",
                                                "id": "annotation-" + data.id
                                              });
        }
        else {
               if (point) {
               var instance = chart.renderer.image('/img/marker.png',
                                            point.plotX + chart.plotLeft - 10,
                                            point.plotY + chart.plotTop -30,
                                            20,
                                            24)
                                     .attr({
                                            "zIndex": 10,
                                            "class": "annotation-marker",
                                            "id": "annotation-" + data.id
                                          });
           }
            else {
                           var instance = chart.renderer.image('/img/marker.png',
                                            chart.plotLeft - 10,
                                            chart.plotTop -30,
                                            20,
                                            24)
                                     .attr({
                                            "zIndex": 10,
                                            "class": "annotation-marker",
                                            "id": "annotation-" + data.id
                                          });
            }
        }

        if($("body").hasClass("hide-annotations")){

            instance.attr({"style": "display:none"});
        }

        instance.add();

        this.$el = $(instance.element);
        this.xPos =  instance.x;
        this.yPos = instance.y;
        this.chart = chart;
        this.point = point;
        this.created = false;

        $("body").append(_get_popover_tmpl(data));

        this.$popover = $("#annotation-popover-" + data.id);
        var get_xpos = function(){

            //xpos is graph xpos  - half popover width - popover borderwidth + x offset
            //var wid_index = $graph[0].outerHTML.indexOf('width');
            //var wid_beg = $graph[0].outerHTML.slice(wid_index+7,wid_index+10);
            //return $graph.offset().left + parseInt(that.$el.attr("x")) - that.$popover.width()/2 - 2 + 20;

            //return $($graph).position().left + parseInt(that.$el.attr("x")) - that.$popover.width()/2 - 2 + 20;
            //return parseInt(that.$el.attr("x")) - that.$popover.width()/2 - 2 + 20;
            return $graph.offset().left + parseInt(that.$el.attr("x")) - that.$popover.width()/2 - 2 + 20;

            //return wid_beg + parseInt(that.$el.attr("x")) + that.$popover.width();

        }

        var get_ypos = function(){

            // ypos is graph ypos - popover height - popover worderwith + y offset
            //return $graph.offset().top + parseInt(that.$el.attr("y")) - that.$popover.height() - 2 + 40;

            //return $($graph).position().top + parseInt(that.$el.attr("y")) - that.$popover.height() - 2 + 40;
            //return parseInt(that.$el.attr("y")) - that.$popover.height() - 2 + 40;
            if (that.new_annotation) {
                return $graph.offset().top +parseInt(that.$el.attr('y')) - that.$popover.height();
            }
            else {
                return $graph.offset().top + parseInt(that.$el.attr("y")) - that.$popover.height() - 2 + 40;
            }
        }
        var on_mouseenter = function(){
            show_annotation(that.new_annotation);
            setCaret(that.$popover.find("p").get(0));
        };

        var on_mouseleave = function(){
            if (that.annot_saved == false){
                swal({
                  title: "Are you sure?",
                  text: "Annotation is not saved. Do you want to save!?",
                  type: "warning",
                  showCancelButton: true,
                  confirmButtonColor: "#DD6B55",
                  confirmButtonText: "Yes, save it!",
                  cancelButtonText: "No, cancel pls!",
                  closeOnConfirm: false,
                  closeOnCancel: false
                }, 

                function(isConfirm){
                    if (isConfirm) {
                        that.save_annotation();
                        swal("Saved!", "Your annotation is saved.", "success");
                    }
                    else {
                        that.$popover.find("p").blur();
                        that.$popover.removeClass("in").removeClass("show");
                        that.destroy();
                        swal("Deleted!", "Your annotation has been deleted.", "success");
                    }
                });
            }
         else {
            that.$popover.find("p").blur();
            $(this).removeClass("in").removeClass("show");
          }
        };

        /*this.cancel_annotation = function(){
            console.log(data);
            that.$popover.find("p").blur();
            $(this).removeClass("in").removeClass("show");
        };*/

        var on_keydown = function(e){

            var yPos = get_ypos();
            that.$popover.css({"top": (yPos) + "px"});
            show_annotation(that.new_annotation);

            if($.inArray(e.which, keydown_whitelist) === -1 && $.inArray(e.which, blacklist_keys) >= 0){
                e.preventDefault();
                return false;
            }

        };

        var update_annotation = function(data){

            return $.post("/api/annotations/update/", data, function(){
            }, "json");
        };

        var on_keyup = function(e){

            if($.inArray(e.which, blacklist_keys) >= 0){
                return false;
            }

            var text = $(this).text();

            var $loading = that.$popover.find("i.annotation-loading").addClass("show");

            data.text = text;
            that.text = text;
            /*if(that.created){
               that.update(data, function(){

                    $loading.removeClass("show");
                });
            }*/

        };

        var save_annotation = function(e){
            that.save_annotation();
        }

        /*var cancel_annotation = function(e){

            that.cancel_annotation();
        }*/

        var delete_annotation = function(e){

            that.delete_annotation();
        };

        var show_annotation = function(vari){

            /*
            var other_series = _.without(that.chart.series, that.point.series);

            $.each(other_series, function(){

                this.hide();
            });
            */

            $("body > div.annotation-popover").filter(".show").removeClass("show");
            if (vari == 'new') {
                var xPos = get_xpos()-8;
                var yPos = get_ypos()+20;
            }
            else {
                var xPos = get_xpos()-10;
                var yPos = get_ypos()-10;
            }
            if (vari == true) {
                var xPos = get_xpos()-8;
                var yPos = get_ypos()+20;
            }
            that.$popover.css({"top": (yPos) + "px", "left": (xPos) + "px"}).addClass("show").addClass("in");
            //that.$popover.css({"top": 99 + "px", "left": 270 + "px"}).addClass("show").addClass("in");

            var $arrow = that.$popover.find("div.arrow").css({"left": "50%"});

            if(xPos < $graph.position().left){


                var diff = $graph.position().left - xPos + 10;

                that.$popover.css({"left": "+="+ diff});

                $arrow.css({"left": "-=" + diff});
            }

            if(xPos + that.$popover.width() > $(window).width()){
                var window_width = $(window).width();

                // 10 is offset
                var popover_position = xPos + that.$popover.width() + 10;

                var diff = popover_position - window_width;

                that.$popover.css({"left": "-="+ diff});

                $arrow.css({"left": "+=" + diff});

            }

            if($(this).parents("#project-sidebar").length > 0){

                setCaret($(this).find("p").get(0));
            }
        };

        if(new_annotation){
            show_annotation('new');
            setCaret(this.$popover.find("p").get(0));
        }

        var hide_annotation = function(){
            /*
            var other_series = _.without(that.chart.series, that.point.series);

            $.each(other_series, function(){

                this.show();
            });
            */
            that.$popover.removeClass("show");
        };

        var redraw = function(){

            that.redraw();
        };

        this.redraw = function(){

            var series_enabled = this.point.series.visible;

            if(!series_enabled){

                this.$el.fadeOut();
                this.$annotations_ul.fadeOut();
            }else{

                this.$el.attr({"y": this.point.plotY + this.chart.plotTop -30, "x": this.point.plotX + this.chart.plotLeft - 10});

                if(!$("body").hasClass("hide-annotations")){
                    this.$el.fadeIn();
                }

                this.$annotations_ul.fadeIn();
            }
        };

        var show_annotation_marker = function(){

            var series_enabled = that.point.series.visible;

            series_enabled ? that.$el.fadeIn(): that.$el.fadeOut();
        };

        var hide_annotation_marker = function(){

            that.$el.fadeOut();
        };

        this.bind_events = function(){

            this.$el.on("mouseenter", on_mouseenter);

            this.$popover.on("mouseleave", on_mouseleave)
                         .on("keydown", "div.popover-content > p", on_keydown)
                         .on("keyup", "div.popover-content > p", on_keyup)
                         .on("click", "span.glyphicon-floppy-disk", save_annotation)
                         .on("click", "span.glyphicon-trash", delete_annotation);
                         //.on("click", "span.glyphicon-remove", cancel_annotation);

            $("body").on(data.graph_name + ".redraw", redraw)
                     .on("annotations.hide", hide_annotation_marker)
                     .on("annotations.show", show_annotation_marker);
        };

        this.bind_events();
        
        this.unbind_events = function(){

            this.$el.off("mouseenter", on_mouseenter);

            this.$popover.off("mouseleave", on_mouseleave)
                         .off("keydown", "div.popover-content > p", on_keydown)
                         .off("keyup", "div.popover-content > p", on_keyup)
                         .off("click", "span.glyphicon-floppy-disk", save_annotation)
                         .off("click", "span.glypglyphicon-trashh", delete_annotation);
                         //.off("click", "span.glyphicon-remove", cancel_annotation);

            $("body").off(data.graph_name + ".redraw", redraw)
                     .off("annotations.hide", hide_annotation_marker)
                     .off("annotations.show", show_annotation_marker);
        }

        _.extend(this, data);

        var update_req = {};

        this.update = function(data, callback){

            if(update_req.abort){
                update_req.abort();
            }

            update_req = update_annotation(data);

            update_req.done(function(){

                update_req = {};
                callback();
            }).fail(function(){

                update_req = {};
                callback();
            });
            return this;
        };

        this.create_annotation = function(data, callback){

            return this.update();
        }
        
        this.destroy = function(){
            this.unbind_events();
            this.collection = _.without(this.collection, this);
            this.$el.remove();
        }

        /*var delete_annotaion = function(){

              swal({
                  title: "Are you sure?",
                  text: "Do you want to delete the annotation!",
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
                    $.post("/api/annotations/update/", _.extend({"action": "delete"}, data), function(resp){
                      if (JSON.parse(resp.result).message == "deleted successfully") {
                        swal("Deleted!", "Your annotation has been deleted.", "success");
                      }
                    });
                  }
                  else {
                    swal("Saved!", "Your annotation is safe.", "success");
                  }
                });
 
            //return $.post("/api/annotations/update/", _.extend({"action": "delete"}, data), function(resp){

            //});
        };*/

        this.save_annotation = function(){

        if(new_annotation){

            this.$popover.find("i.annotation-loading").addClass("show");

            $.post("/api/annotations/create/", data, function(resp){

                if (resp.result == 'Annotation already exist'){
                        swal(resp.result);
                        that.$popover.find("p").blur();
                        that.$popover.removeClass("in").removeClass("show");
                        that.destroy();
                        return;
                }

                resp = resp.result;

                var id = resp.id,
                    old_id = that.id;

                data.id  = id;

                that.$el.attr({"id": that.$el.attr("id").replace(old_id, id)});
                that.$popover.attr({"id": that.$popover.attr("id").replace(old_id, id)});

                that.created = true;

            }).fail(function(){

                buzz_data.utils.show_message("Unable to create annotation");
                that.delete_annotation();
            }).always(function(){

                that.$popover.find("i.annotation-loading").removeClass("show");
            }).then(function() {
               $.post("/api/annotations/update/", _.extend({"action": "update"}, data), function(resp){

               if (JSON.parse(resp).message == "successfully updated") {

                    that.annot_saved = true;

                    }
               });

            });
        }else{

            this.created = true;
         }

            /*return $.post("/api/annotations/update/", _.extend({"action": "update"}, data), function(resp){
                
               if (JSON.parse(resp).message == "successfully updated") {
                
                    that.annot_saved = true;
                   
                }
            });*/
        };

        this.delete_annotation = function(callback) {

            this.destroy();

              swal({
                  title: "Are you sure?",
                  text: "Do you want to delete the annotation!",
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
                    $.post("/api/annotations/update/", _.extend({"action": "delete"}, data), function(resp){
                      if (JSON.parse(resp.result).message == "deleted successfully") {
                        that.$popover.remove();
                        that.$el.remove();
                        swal("Deleted!", "Your annotation has been deleted.", "success");
                        
                      }
                    });
                  }
                  else {
                    swal("Saved!", "Your annotation is safe.", "success");
                  }
                });

                

            /*var delete_annotation = delete_annotaion();

            var $loading = this.$popover.find("i.annotation-loading").addClass("show");

            delete_annotation.done(function(){

                $loading.removeClass("show");
                that.$popover.remove();
                that.$el.remove();

            }).fail(function(){

                buzz_data.utils.show_message("Unable to delete annotation");
                $loading.removeClass("show");
                that.bind_events();
            });*/

            return this;
        }

       /* if(new_annotation){

            this.$popover.find("i.annotation-loading").addClass("show");

            $.post("/api/annotations/create/", data, function(resp){

                resp = resp.result;

                var id = resp.id,
                    old_id = that.id;

                data.id  = id;

                that.$el.attr({"id": that.$el.attr("id").replace(old_id, id)});
                that.$popover.attr({"id": that.$popover.attr("id").replace(old_id, id)});

                that.created = true;

            }).fail(function(){

                buzz_data.utils.show_message("Unable to create annotation");
                that.delete_annotation();
            }).always(function(){

                that.$popover.find("i.annotation-loading").removeClass("show");
            });
        }else{

            this.created = true;
        }*/

        this.collection.push(this);

    };

    Annotation.prototype.collection = [];

    $(function () {
      _get_popover_tmpl = _.template($("#annotation-popover-tmpl").text());
    });
}(window.jQuery));
