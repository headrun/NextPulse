;(function($){
    "use strict";

    var _ = window._;

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
        // $(el).focus().trigger("click");

        return el;
    }

    buzz_data.utils = {"show_message": function(msg) {window.alert(msg);}};


    var Annotation = buzz_data.Annotation = function(graph_name, $graph, chart, point, data){

        graph_name = graph_name || "overview";

        var that = this;        
        
        var new_annotation = !data;

        var on_text_change = false;
        var text_container = "";
        var wid_day_type = "";

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
            data["day_type"] = graph_name.split('<##>')[1];
            data["project"] = point.project;
            data["center"] = point.center;
            data["from"] = point.from;
            data["to"] = point.to;
            data["chart_type"] = point.chart_type;
            
        }
        else{
            that.annot_saved = false;           
        }

        if (point.barX) {
            var instance = chart.renderer.image('/img/marker.png',
                                                point.barX+(point.pointWidth/2) + chart.plotLeft - 10,
                                                point.plotY - 10,
                                                20,
                                                24)
                                         .attr({
                                                "zIndex": 10,
                                                "class": "annotation-marker",
                                                "id": "annotation-" + data.id,
                                                "series-name": point.series.name,
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
                                            "id": "annotation-" + data.id,
                                            "series-name": point.series.name,
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
                                            "id": "annotation-" + data.id,
                                            "series-name": point.series.name,
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

            return $graph.offset().left + parseInt(that.$el.attr("x")) - that.$popover.width()/2 - 2 + 20;

        }
        that.on_text_change = false;
        that.text_container = data.text.trim();


        var get_ypos = function(){

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
            if(data.text.trim() != ''){ 
                if(that.new_annotation){
                    if (that.annot_saved !== true){
                        swal({
                        title: "Annotation is not saved yet!",
                        text: "Do you want to save it?",
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Yes, Save it!",
                        cancelButtonText: "No, Delete pls!",
                        closeOnConfirm: false,
                        closeOnCancel: false
                        }, 

                        function(isConfirm){
                            if (isConfirm) {
                                that.save_annotation();
                                that.$popover.removeClass("in").removeClass("show");
                                swal("Saved!", "Your annotation is saved.", "success");
                            }
                            else {
                                that.$popover.find("p").blur();
                                that.$popover.removeClass("in").removeClass("show");
                                that.destroy();
                                swal("Deleted!", "Your annotation has been deleted.", "success");
                            }
                        });
                        that.$popover.find("p").blur();
                        $(this).removeClass("in").removeClass("show");                        
                    } else {
                        that.$popover.find("p").blur();                        
                        $(this).removeClass("show");
                    }
                }
                else{                   
                    if(that.annot_saved !== true && that.on_text_change === true){
                        swal({
                            title: 'Annotation has been edited!',
                            text: "Do you want to save it?",
                            type: "warning",
                            showCancelButton: true,
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "Yes, Save it!",
                            cancelButtonText: "No, Don't Save it!",
                            closeOnConfirm: false,
                            },
                            function(isConfirm) {
                                if (isConfirm) {
                                    that.save_annotation();
                                    that.$popover.removeClass("in").removeClass("show");
                                    that.reset();
                                    swal("Updated!", "Your Changes are Updated.", "success");
                                }
                                else {                                    
                                    that.$popover.find("p").get(0).innerHTML = that.text_container;                                    
                                    setCaret(that.$popover.find("p").get(0));
                                    that.$popover.find("p").blur();
                                    that.$popover.removeClass("in").removeClass("show");                                                                          
                                    that.reset();                                    
                                }
                            });                       
                    
                }else {
                    that.reset();
                    that.$popover.find("p").blur();
                    that.$popover.removeClass("in").removeClass("show");                        
                }
            }
            } else {                
                
                swal({
                    title: "Annotation is Empty!",
                    text: "Do you want to continue typing?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, Continue it!",
                    cancelButtonText: "No, Delete pls!",
                    closeOnConfirm: false,
                    },
                    function(isConfirm) {
                        if (isConfirm) {
                            setCaret(that.$popover.find("p").get(0));
                            $(".showSweetAlert,.sweet-overlay").attr("style","display:none");
                        }
                        else {
                            that.$popover.find("p").blur();
                            that.$popover.removeClass("in").removeClass("show");
                            that.destroy();
                            swal("Deleted!", "Your annotation is deleted.", "success");
                        }
                    });

            }
        };

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
            that.on_text_change = true;           

            var $loading = that.$popover.find("i.annotation-loading").addClass("show");

            data.text = text;
            that.text = text;            

        };

        var save_annotation = function(e){
            if(data.text.trim() != ''){
                that.save_annotation(true);
            }
        }


        var delete_annotation = function(e){

            that.delete_annotation();
        };

        var show_annotation = function(vari){            

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
            
            var $arrow = that.$popover.find("div.arrow").css({"left": "50%"});

            if(xPos < $graph.position().left){

                var diff = $graph.position().left - xPos + 10;

                that.$popover.css({"left": "+="+ diff});

                $arrow.css({"left": "-=" + diff});
            }

            if(xPos + that.$popover.width() > $(window).width()){
                var window_width = $(window).width();
                
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
            let selector = this.$popover.selector;
            if(selector.split("-")[3] != 1 ){
                let val_id = selector.split("-")[3]
                for(var all_gen_id=1;all_gen_id < parseInt(val_id);all_gen_id++){
                    if($('#annotation-annotation-'+all_gen_id)[0] != undefined){
                        if($('#annotation-popover-annotation-'+all_gen_id+' p').text().trim().length > 0){
                                
                                for (var rem = all_gen_id + 1; rem <= parseInt(val_id); rem++){
                                    $('#annotation-popover-annotation-'+(rem)).remove();
                                    $("#annotation-annotation-"+(rem)).remove();
                                }
                                
                                $("#annotation-popover-annotation-"+(all_gen_id)).addClass("show");                                
                                swal("Please Save Previous Annotation ");                            
                        
                        } 
                        else
                         {
                            $("#annotation-annotation-"+all_gen_id).remove();
                            $('#annotation-popover-annotation-'+all_gen_id).remove();                            
                            setCaret(this.$popover.find("p").get(0));    
                        }
                    }
            
                }
            }
            else{
                setCaret(this.$popover.find("p").get(0));
                
            }
        }          
        

        var hide_annotation = function(){
            
            that.$popover.removeClass("show");
        };

        var redraw = function(){

            that.redraw();
        };

        

        this.redraw = function(seriesname, visible){


            var series_enabled = visible;

            if(!series_enabled){

                if (point.barX) {                   
                    this.$el.attr({"y": point.plotY - 10, "x": point.barX+(point.pointWidth/2) + chart.plotLeft - 10});
                }
                else {
                    this.$el.attr({"y": this.point.plotY + this.chart.plotTop -30, "x": this.point.plotX + this.chart.plotLeft - 10});
                }
                
            } else{
                if (point.barX) {
                    this.$el.attr({"y": point.plotY - 10, "x": point.barX+(point.pointWidth/2) + chart.plotLeft - 10});
                }
                else{
                    this.$el.attr({"y": this.point.plotY + this.chart.plotTop -30, "x": this.point.plotX + this.chart.plotLeft - 10});
                }
                if(!$("body").hasClass("hide-annotations")){
                    this.$el.fadeIn();
                }
                
                this.$el.fadeIn();
            }
        };

        var show_annotation_marker = function(){

            var series_enabled = that.point.series.visible;

            series_enabled ? that.$el.fadeIn(): that.$el.fadeOut();
        };

        var hide_annotation_marker = function(){

            that.$el.fadeOut();
        };

        this.reset = function(){
            that.on_text_change = false;
            that.annot_saved = false;     
        };

        this.bind_events = function(){

            this.$el.on("mouseenter", on_mouseenter);
            this.$popover.on("mouseleave", on_mouseleave)
                         .on("keydown", "div.popover-content > p", on_keydown)                         
                         .on("keyup", "div.popover-content > p", on_keyup)                         
                         .on("click", "span.glyphicon-floppy-disk", function(){
                               save_annotation(true);
                            })
                         .on("click", "span.glyphicon-trash", delete_annotation);
                         

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
                         .off("click", "span.glypglyphicon-trash", delete_annotation);
                         

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

        
        this.destroy = function(){
            this.unbind_events();
            this.collection = _.without(this.collection, this);
            this.$el.remove();
        }


        this.save_annotation = function(disk_click_flag = false){           
                
            if(data.text.trim() != ''){
                
                if(new_annotation){            
                    
                    $.post("/api/annotations/create/", data, function(resp){                    
                    
                        that.annot_saved = true; 
                        resp = resp.result;
                        if(resp == 'Annotation already exist'){
                            that.showAlert('Annotation already exist! Please try with an another text');
                            return true;
                        }
                        var id = resp.id,
                            old_id = that.id;

                        data.id  = id;
                        that.$el.attr({"id": that.$el.attr("id").replace(old_id, id)});
                        that.$popover.attr({"id": that.$popover.attr("id").replace(old_id, id)});
                        that.created = true;
                        
                        if(disk_click_flag){
                            that.showAlert('Your annotation has been saved successfully');
                        }

                        let fetch_date_type = data['graph_name'].split('<##>')[1];                        
                        if (fetch_date_type == "month"){
                            $(".widget-body.widget-"+data['widget_id']+"b #Month")[0].click();    
                        } else {
                            $(".widget-body.widget-"+data['widget_id']+"b #"+fetch_date_type)[0].click();
                        }
                        
                        

                    }).fail(function(){
                        $.post("/api/annotations/update/", _.extend({"action": "update"}, data), function(resp){

                    if (JSON.parse(resp).message == "successfully updated") {
                            that.annot_saved = true;
                            }
                    });
                    
                    });
                }
                else {

                    that.created = true;
                    that.text_container = data.text.trim();                
                
                    return $.post("/api/annotations/update/", _.extend({"action": "update"}, data), function(resp){
                        
                    if (JSON.parse(resp).message == "successfully updated") {
                        
                            that.annot_saved = false;

                            if(disk_click_flag){
                                that.$popover.find("p").blur();
                                that.$popover.removeClass("in").removeClass("show");
                                that.showAlert('Annotation has been updated successfully');                                                               
                            }
                        
                        }
                    });
                    
                }
            } else {                
                that.destroy();            
            }
        };

        

        this.showAlert = function(msg){
          swal({
              title: msg,
              type: "success",
              showConfirmButton: true,
              confirmButtonColor: "#DD6B55",
              closeOnConfirm: true,
          });  
        } 

        

        this.delete_annotation = function() {            

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
                    if (data.text != "") {
                        swal("Saved!", "Your annotation is safe.", "success");
                        on_mouseleave();    
                        console.log(point.series.name);
                    } else {
                        $.post("/api/annotations/create/", data, function(resp){
                            that.save_annotation();
                            on_mouseleave();
                            $('.annotation-marker').show();
                            $(document).find('.annotation-marker[series-name="'+point.series.name+'"]').show();
                            console.log(point.series.name);
                        });   
                    }
                  }
                });          

            return this;
        }

       

        this.collection.push(this);

    };

    Annotation.prototype.collection = [];

    $(function () {
      _get_popover_tmpl = _.template($("#annotation-popover-tmpl").text());
    });
}(window.jQuery));
