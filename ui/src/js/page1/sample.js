var app = angular.module('sample', []);
app.controller('sampleCtrl', function($scope, $http){
  $(window).on('load', function(){
    $('#loader').show();
  });
  $scope.sa_url = window.location.href;
  $scope.sa_url_split = $scope.sa_url.split('&');
  $scope.start_date = $scope.sa_url_split[3].split('=')[1]
  $scope.end_date = $scope.sa_url_split[4].split('=')[1]
  $scope.url = '/api/historical_packet_agent/?widget_data=&'+$scope.sa_url_split[1]+'&'+$scope.sa_url_split[2]+'&'+$scope.sa_url_split[3]+'&'+$scope.sa_url_split[4];
  $http({method:'GET', url:$scope.url}).then(function(result){
    $('#loader').hide();
    $('#formData').slideDown(200);
    $('#formData').attr('class', 'modal fade in');
    $('#formData').css('display', 'block');
    $("<div class='modal-backdrop fade in'></div>").insertAfter('#formData');
    $(".close-sample-form").click(function(){
      $('#formData').slideUp(300);
      $('.modal-backdrop').remove();
    });
    $scope.packet_data = result.data.config_packets;
    $scope.agent_data = result.data.config_agents;
    $scope.rem_packets = result.data.packets;
    $scope.rem_agents = result.data.agents;
    $scope.packet_config_value = result.data.packet_value;
    $scope.agent_config_value = result.data.agent_value;
    }, function(error){
          $('.modal-backdrop').remove();
          $('.error-msg').delay(500).fadeOut();
  });

  dragula([document.getElementById('dragger-packet')],{removeOnSpill:true}).on('out', function(el, target, container, source){
      $scope.packets_elements = el.parentElement.parentElement.children['0'].children;
      for (var i = 0; i<$scope.packets_elements.length; i++){
        if(el === $scope.packets_elements[i]){
          $scope.el_id = el.children['0'].id;
          $scope.rm_el_index = i;
          $scope.rm_el_data = el.innerText.trim();
          $scope.rem_packets.push($scope.rm_el_data);
          break;
        }
      }
    });

    $scope.add_packet = function(){
      var new_packet = document.getElementById('newpacket').value;

      // This if will execute when the packet is not selected and directly when we click plus button.
      if($scope.rm_el_index == undefined || $scope.packets_elements.length === $scope.packet_config_value){
        var rm_el_id = $("#dragger-packet").children().last()['0'].firstElementChild.id;
        var rm_el_data = $('#dragger-packet').children().last()['0'].firstElementChild.innerText;
        var i = $scope.rem_packets.indexOf(new_packet);
        $scope.rem_packets.splice(i, 1);
        $scope.rem_packets.push(rm_el_data);
        var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+rm_el_id+")' data-toggle='modal' data-target='#addpacket-card'>\
                      <p style='margin-top:10px;text-align:center;' id="+rm_el_id+">"+new_packet+"</p>\
                  </div>";
        var pl = $('#dragger-packet').children().length;
        if(pl=== $scope.packet_config_value){
          $("#dragger-packet").children().last().remove();
          $(el).prependTo('#dragger-packet');
        }

      // This else will execute when the packet is  and after plus button is clicked.
      }else if($scope.rm_el_index !== undefined){
          var pl = $('#dragger-packet').children().length;
          if($scope.rm_el_index==pl){
            var i = $scope.rem_packets.indexOf(new_packet);
            $scope.rem_packets.splice(i, 1);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+$scope.rm_el_id+")' data-toggle='modal' data-target='#addpacket-card'>\
                      <p style='margin-top:10px;text-align:center;' id="+$scope.rm_el_id+">"+new_packet+"</p>\
                  </div>";
            $('#dragger-packet').append(el);
            // This else if will execute when the no packet was removed still the packet
            // was try to removed and plus button is clicked, it will replace the last packet with new one. 
          }else if(pl == $scope.packet_config_value ){
            var rm_el_id = $("#dragger-packet").children().last()['0'].firstElementChild.id;
            var rm_el_data = $('#dragger-packet').children().last()['0'].firstElementChild.innerText;
            var i = $scope.rem_packets.indexOf(new_packet);
            $scope.rem_packets.splice(i, 1);
            $scope.rem_packets.push(rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+rm_el_id+")' data-toggle='modal' data-target='#addpacket-card'>\
                          <p style='margin-top:10px;text-align:center;' id="+rm_el_id+">"+new_packet+"</p>\
                      </div>";
            var pl = $('#dragger-packet').children().length;
            if(pl=== $scope.packet_config_value){
              $("#dragger-packet").children().last().remove();
              $("#dragger-packet").append(el);
            }else{
              $("#dragger-packet").append(el);
            }
          }else if(pl != $scope.packet_config_value){
            var temp = [];
            // This if executes when the packet is not first one.
            if($scope.rm_el_index != 0){
              var temp_index = 0;
              for (var i=0; i<$scope.rm_el_index; i++){
                temp.push($scope.packets_elements[i]);
                temp_index = i;
              }
              var i = $scope.rem_packets.indexOf(new_packet);
              $scope.rem_packets.splice(i, 1);
              var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+$scope.rm_el_id+")' data-toggle='modal' data-target='#addpacket-card'>\
                          <p style='margin-top:10px;text-align:center;' id="+$scope.rm_el_id+">"+new_packet+"</p>\
                      </div>";
              temp.push(el);
              temp_index+=1
              for (temp_index; temp_index<$scope.packets_elements.length; temp_index++){
                temp.push($scope.packets_elements[temp_index])
              }
              $('#dragger-packet').children().remove();
              $('#dragger-packet').append(temp);
            }else{
              var i = $scope.rem_packets.indexOf(new_packet);
              $scope.rem_packets.splice(i, 1);
              var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+$scope.rm_el_id+")' data-toggle='modal' data-target='#addpacket-card'>\
                          <p style='margin-top:10px;text-align:center;' id="+$scope.rm_el_id+">"+new_packet+"</p>\
                      </div>";
              $(el).prependTo('#dragger-packet');
            }
          }
      }
    }

    $scope.simple = function(p_id){
      $scope.p_id = p_id;
      $scope.p_data = document.getElementById(p_id).innerText;
    }

    $scope.add_packet_card = function(){
      var new_packet_data = document.getElementById('newpacketcard').value;
      document.getElementById($scope.p_id).innerText=new_packet_data;
      var index = $scope.rem_packets.indexOf(new_packet_data);
      $scope.rem_packets.splice(index, 1);
      $scope.rem_packets.push($scope.p_data);
    }

    $scope.autocomplete = function(inp, arr) {
      var inp = document.getElementById(inp);
      if(arr == undefined){arr=$scope.rem_agents}
      var currentFocus;
      inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        closeAllLists();
          if (!val) { return false;}
          currentFocus = -1;
          a = document.createElement("DIV");
          a.setAttribute("id", this.id + "autocomplete-list");
          a.setAttribute("class", "autocomplete-items");
          this.parentNode.appendChild(a);
          for (var i = 0; i < arr.length; i++) {
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
              b = document.createElement("DIV");
              b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
              b.innerHTML += arr[i].substr(val.length);
              b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
              b.addEventListener("click", function(e) {
                  inp.value = this.getElementsByTagName("input")[0].value;
                  closeAllLists();
              });
              a.appendChild(b);
            }
          }
      });
      inp.addEventListener("keydown", function(e) {
          var x = document.getElementById(this.id + "autocomplete-list");
          if (x) x = x.getElementsByTagName("div");
          if (e.keyCode == 40) {
            currentFocus++;
            addActive(x);
          } else if (e.keyCode == 38) { 
            currentFocus--;
            addActive(x);
          } else if (e.keyCode == 13) {
            e.preventDefault();
            if (currentFocus > -1) {
              if (x) x[currentFocus].click();
            }
          }
      });
      function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
      }
      function removeActive(x) {
        for (var i = 0; i < x.length; i++) {
          x[i].classList.remove("autocomplete-active");
        }
      }
      function closeAllLists(elmnt) {
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
          if (elmnt != x[i] && elmnt != inp) {
            x[i].parentNode.removeChild(x[i]);
          }
        }
      }
      document.addEventListener("click", function (e) {
          closeAllLists(e.target);
      });
    }

    $scope.add_agent_card = function(){
      var newagent = document.getElementById('newagentcard').value;
      var el = document.getElementById($scope.p_id);
      el.innerText = newagent;
      var index = $scope.rem_agents.indexOf(newagent);
      $scope.rem_agents.splice(index, 1);
      $scope.rem_agents.push($scope.p_data);
    }

    dragula([document.getElementById('dragger-agent')],{removeOnSpill:true}).on('out', function(el, target, container, source){
      $scope.agents_elements = el.parentElement.children;
      for (var i = 0; i<$scope.agents_elements.length; i++){
        if(el === $scope.agents_elements[i]){
          $scope.a_el_id = el.children['0'].id;
          $scope.a_rm_el_index = i;
          $scope.a_rm_el_data = el.innerText.trim();
          $scope.rem_agents.push($scope.a_rm_el_data);
          break;
        }
      }
    });

    $scope.add_agent = function(){
      var new_agent = document.getElementById('newagent').value;
      // This if will execute when the packet is not selected and directly when we click plus button.
      if($scope.a_rm_el_index == undefined || $scope.agents_elements.length === $scope.agent_config_value){
        var rm_el_id = $("#dragger-agent").children().last()['0'].firstElementChild.id;
        var rm_el_data = $('#dragger-agent').children().last()['0'].firstElementChild.innerText;
        var i = $scope.rem_agents.indexOf(new_agent);
        $scope.rem_agents.splice(i, 1);
        $scope.rem_agents.push(rm_el_data);
        var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+rm_el_id+")' data-toggle='modal' data-target='#addagent-card'>\
                      <p style='margin-top:10px;text-align:center;' id="+rm_el_id+">"+new_agent+"</p>\
                  </div>";
        var pl = $('#dragger-agent').children().length;
        if(pl=== $scope.packet_config_value){
          $("#dragger-agent").children().last().remove();
          $(el).prependTo("#dragger-agent");
        }
      // This else if will execute when the packet is dragged and after plus button is clicked.
      }else if($scope.a_rm_el_index !== undefined){
          var pl = $('#dragger-agent').children().length;
          if($scope.a_rm_el_index==pl){
            var i = $scope.rem_agents.indexOf(new_agent);
            $scope.rem_agents.splice(i, 1);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+$scope.a_rm_el_id+")' data-toggle='modal' data-target='#addagent-card'>\
                      <p style='margin-top:10px;text-align:center;' id="+$scope.a_rm_el_id+">"+new_agent+"</p>\
                  </div>";
            $('#dragger-agent').append(el);
            // This else if will execute when the no packet was removed still the packet
            // was try to removed and plus button is clicked, it will replace the last packet with new one. 
          }else if(pl == $scope.agent_config_value ){
            var rm_el_id = $("#dragger-agent").children().last()['0'].firstElementChild.id;
            var rm_el_data = $('#dragger-agent').children().last()['0'].firstElementChild.innerText;
            var i = $scope.rem_agents.indexOf(new_agent);
            $scope.rem_agents.splice(i, 1);
            $scope.rem_agents.push(rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+rm_el_id+")' data-toggle='modal' data-target='#addagent-card'>\
                          <p style='margin-top:10px;text-align:center;' id="+rm_el_id+">"+new_agent+"</p>\
                      </div>";
            var pl = $('#dragger-agent').children().length;
            if(pl=== $scope.agent_config_value){
              $("#dragger-agent").children().last().remove();
              $("#dragger-agent").append(el);
            }else{
              $("#dragger-agent").append(el);
            }
          }else if(pl != $scope.agent_config_value){
            var temp = [];
            // This if executes when the packet is not first one.
            if($scope.a_rm_el_index != 0){
              var temp_index = 0;
              for (var i=0; i<$scope.a_rm_el_index; i++){
                temp.push($scope.agents_elements[i]);
                temp_index = i;
              }
              var i = $scope.rem_agents.indexOf(new_agent);
              $scope.rem_agents.splice(i, 1);
              var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+$scope.a_rm_el_id+")' data-toggle='modal' data-target='#addagent-card'>\
                          <p style='margin-top:10px;text-align:center;' id="+$scope.a_rm_el_id+">"+new_agent+"</p>\
                      </div>";
              temp.push(el);
              temp_index+=1
              for (temp_index; temp_index<$scope.agents_elements.length; temp_index++){
                temp.push($scope.agents_elements[temp_index])
              }
              $('#dragger-agent').children().remove();
              $('#dragger-agent').append(temp);
            }else{
              var i = $scope.rem_agents.indexOf(new_agent);
              $scope.rem_agents.splice(i, 1);
              var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll', ng-click='$ctrl.simple("+$scope.a_rm_el_id+")' data-toggle='modal' data-target='#addagent-card'>\
                          <p style='margin-top:10px;text-align:center;' id="+$scope.a_rm_el_id+">"+new_agent+"</p>\
                      </div>";
              $(el).prependTo('#dragger-agent');
            }
          }
      }
    }

    $scope.formData = function(){
            $scope.audit_per = document.getElementById('audit').value;
            $scope.random_per = document.getElementById('randomsample').value;
            var packets_ids = [];
            var agents_ids = [];
            var total_packets = $('#dragger-packet').children().length;
            for(var i = 1; i<=total_packets; i++){
              packets_ids.push("packet"+i);
            }

            var total_agents = $('#dragger-agent').children().length;
            for(var i = 1; i<=total_agents; i++){
              agents_ids.push("agent"+i);
            }
            var packets_data = new Array(total_packets);
            var agents_data = new Array(total_agents);

            for(var i = 0; i<packets_ids.length; i++)
                packets_data[i] = document.getElementById(packets_ids[i]).innerText;

            for(var j = 0; j<agents_ids.length; j++)
                agents_data[j] = document.getElementById(agents_ids[j]).innerText;

            var center = $scope.sa_url_split[2].split('=')[1]
            var project = $scope.sa_url_split[1].split('=')[1]
            project = project.replace(/%20/g, ' ');
            var url = "/api/packet_agent_audit_random/";
            var data = {'packets':packets_data, 'agents':agents_data, 'audit':$scope.audit_per, 'random':$scope.random_per, 'from':$scope.start_date, 'to':$scope.end_date, 'project':project, 'center':center};


            $http({method:'POST', url:url, data:data, headers:{'Content-Type':'application/x-www-form-urlencoded;charset=utf-8;'}}).then(function(result){
                $scope.success = true;
                $('#audit').val($scope.audit_per);
                $('randomsample').val($scope.random_per);
                $scope.excel_data = result.data;
            });
    }

    $scope.download_excel = function(){
        var url = "/api/download_audit_excel/";
        $http({method:'POST', url:url, data:$scope.excel_data, responseType: "blob", headers:{'Content-Type':'application/x-www-form-urlencoded;charset=utf-8;'}}).then(function(result){

           const url = window.URL.createObjectURL(new Blob([result.data]));
           const link = document.createElement('a');
           link.href = url;
           link.setAttribute('download', 'audit_data.xlsx');
           document.body.appendChild(link);
           link.click();
        });
    }
});
