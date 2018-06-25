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
    $scope.packet_data = result.data.config_packets;
    $scope.agent_data = result.data.config_agents;
    $scope.rem_packets = result.data.packets;
    $scope.rem_agents = result.data.agents;
    $scope.packet_config_value = result.data.packet_value;
    $scope.agent_config_value = result.data.agent_value;
    $scope.total_production = result.data.total_production;
    }, function(error){
          $('.modal-backdrop').remove();
          $('.error-msg').delay(500).fadeOut();
  });

  dragula([document.getElementById('dragger-packet')],{removeOnSpill:true}).on('out', function(el, target, container, source){
      $scope.packets_elements = el.parentElement.parentElement.children['0'].children;
      $scope.p_size = $scope.packets_elements.length;
      for (var i = 0; i<$scope.packets_elements.length; i++){
        if(el === $scope.packets_elements[i]){
          $scope.el_id = el.children['0'].id;
          $scope.rm_el_index = i;
          $scope.rm_el_data = el.innerText.trim();
          $scope.p_size -= 1;
          break;
        }
      }
    });

    $scope.add_packet_cnf = function(){
      if($scope.rem_packets.length === 0 && $scope.rem_agents.length !== 0){
        swal({
          title:'info',
          text:'No Packets, Please select agents...',
          icon:'info',
          button:'ok'
        });
        return;
      }else if($scope.rem_packets.length === 0 && $scope.rem_agents.length === 0){
        swal({
          title:'info',
          text:'No Agents or Packets',
          icon:'info',
          button:'ok'
        });
      }else{
        $('#addpacket').show();
        $('#addpacket').attr('class', 'modal fade in');
        $('#addpacket').css('display', 'block');
      }
    }
    $(".close-add-packet").click(function(){
      $('#addpacket').slideUp(300);
    });
    $scope.add_packet = function(){
      
      var new_packet = document.getElementById('newpacket').value;
      var pl = $('#dragger-packet').children().length;

      // This 'if' block will execute when the packet is not selected and directly when we click plus button.
      if($scope.rm_el_index == undefined){
        var i = $scope.rem_packets.indexOf(new_packet);
        $scope.rem_packets.splice(i, 1);
        var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll'>\
                      <p style='margin-top:10px;text-align:center;'>"+new_packet+"</p>\
                  </div>";
        $(el).prependTo('#dragger-packet');

        // This 'elseif ' block will execute when the rm_el_index is not undefined.
      }else if($scope.rm_el_index != undefined){
          var pl = $('#dragger-packet').children().length;

          // This 'elseif' block will execute when the last packet is removed and plus button is clicked.
          if($scope.rm_el_index != undefined && $scope.rm_el_index === pl){
            var i = $scope.rem_packets.indexOf(new_packet);
            $scope.rem_packets.splice(i, 1);
            $scope.rem_packets.push($scope.rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll'>\
                      <p style='margin-top:10px;text-align:center;'>"+new_packet+"</p>\
                  </div>";
            $('#dragger-packet').append(el);
            $scope.rm_el_index = undefined;
          }else if($scope.p_size === pl && ($scope.rm_el_index != undefined && $scope.rm_el_index !== 0)){
            var temp = [];
            // This if executes when the packet is not first one.
            var temp_index = 0;
            for (var i=0; i<$scope.rm_el_index; i++){
              temp.push($scope.packets_elements[i]);
              temp_index = i;
            }
            var i = $scope.rem_packets.indexOf(new_packet);
            $scope.rem_packets.splice(i, 1);
            $scope.rem_packets.push($scope.rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll'>\
                        <p style='margin-top:10px;text-align:center;'>"+new_packet+"</p>\
                    </div>";
            temp.push(el);
            temp_index+=1
            for (temp_index; temp_index<$scope.packets_elements.length; temp_index++){
              temp.push($scope.packets_elements[temp_index])
            }
              $('#dragger-packet').children().remove();
              $('#dragger-packet').append(temp);
              $scope.rm_el_index = undefined;
          }else if(($scope.rm_el_index != undefined && $scope.rm_el_index === 0) || $scope.p_size !== pl){
              var i = $scope.rem_packets.indexOf(new_packet);
              $scope.rem_packets.splice(i, 1);
              var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll'>\
                          <p style='margin-top:10px;text-align:center;'>"+new_packet+"</p>\
                      </div>";
              $(el).prependTo('#dragger-packet');
              $scope.rm_el_index = undefined;

          /* This 'elseif' block will execute when the no packet was removed still the packet
              was dragged and plus button is clicked, it will replace the last packet with new one. */
          }else if($scope.rm_el_index != undefined && pl !== $scope.packet_config_value ){
            var i = $scope.rem_packets.indexOf(new_packet);
            $scope.rem_packets.splice(i, 1);
            $scope.rem_packets.push($scope.rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.packet_data' style='margin-top: -10px; cursor:all-scroll'>\
                          <p style='margin-top:10px;text-align:center;'>"+new_packet+"</p>\
                      </div>";
            $(el).prependTo("#dragger-packet");
            $scope.rm_el_index = undefined;
          }
      }
    };

    // $scope.simple = function(p_id){
    //   $scope.p_id = p_id;
    //   $scope.p_data = document.getElementById(p_id).innerText;
    // }

    // $scope.add_packet_card = function(){
    //   var new_packet_data = document.getElementById('newpacketcard').value;
    //   document.getElementById($scope.p_id).innerText=new_packet_data;
    //   var index = $scope.rem_packets.indexOf(new_packet_data);
    //   $scope.rem_packets.splice(index, 1);
    //   $scope.rem_packets.push($scope.p_data);
    // }

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

    // $scope.add_agent_card = function(){
    //   var newagent = document.getElementById('newagentcard').value;
    //   var el = document.getElementById($scope.p_id);
    //   el.innerText = newagent;
    //   var index = $scope.rem_agents.indexOf(newagent);
    //   $scope.rem_agents.splice(index, 1);
    //   $scope.rem_agents.push($scope.p_data);
    // }

    dragula([document.getElementById('dragger-agent')],{removeOnSpill:true}).on('out', function(el, target, container, source){
      $scope.agents_elements = el.parentElement.children;
      $scope.a_size = $scope.agents_elements.length;
      for (var i = 0; i<$scope.agents_elements.length; i++){
        if(el === $scope.agents_elements[i]){
          $scope.a_el_id = el.children['0'].id;
          $scope.a_rm_el_index = i;
          $scope.a_rm_el_data = el.innerText.trim();
          $scope.a_size -= 1;
          break;
        }
      }
    });

    $scope.add_agent_cnf = function(){
      if($scope.rem_packets.length !== 0 && $scope.rem_agents.length === 0){
        swal({
          title:'info',
          text:'No Agents, Please select packets...',
          icon:'info',
          button:'ok'
        });
        return;
      }else if($scope.rem_packets.length === 0 && $scope.rem_agents.length === 0){
        swal({
          title:'info',
          text:'No Agents or Packets',
          icon:'info',
          button:'ok'
        });
      }else{
        $('#addagent').show();
        $('#addagent').attr('class', 'modal fade in');
        $('#addagent').css('display', 'block');
      }
    }

    $(".close-add-agent").click(function(){
      $('#addagent').slideUp(300);
    });

    $scope.add_agent = function(){
      var new_agent = document.getElementById('newagent').value;

      // This if will execute when the packet is not selected and directly when we click plus button.
      if($scope.a_rm_el_index == undefined){
        var i = $scope.rem_agents.indexOf(new_agent);
        $scope.rem_agents.splice(i, 1);
        var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll'>\
                      <p style='margin-top:10px;text-align:center;'>"+new_agent+"</p>\
                  </div>";
        $(el).prependTo("#dragger-agent");

      // This else if will execute when the packet is dragged and after plus button is clicked.
      }else if($scope.a_rm_el_index !== undefined){
          var al = $('#dragger-agent').children().length;

          if($scope.a_rm_el_index !== undefined && $scope.a_rm_el_index === al){
            var i = $scope.rem_agents.indexOf(new_agent);
            $scope.rem_agents.splice(i, 1);
            $scope.rem_agents.push($scope.a_rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll'>\
                      <p style='margin-top:10px;text-align:center;'>"+new_agent+"</p>\
                  </div>";
            $('#dragger-agent').append(el);
            $scope.a_rm_el_index = undefined;

          }else if($scope.a_size === al && ($scope.a_rm_el_index != undefined && $scope.a_rm_el_index !== 0)){
            var temp = [];
            var temp_index = 0;
            for (var i=0; i<$scope.a_rm_el_index; i++){
              temp.push($scope.agents_elements[i]);
              temp_index = i;
            }
            var i = $scope.rem_agents.indexOf(new_agent);
            $scope.rem_agents.splice(i, 1);
            $scope.rem_agents.push($scope.a_rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll'>\
                        <p style='margin-top:10px;text-align:center;'>"+new_agent+"</p>\
                    </div>";
            temp.push(el);
            temp_index+=1
            for (temp_index; temp_index<$scope.agents_elements.length; temp_index++){
              temp.push($scope.agents_elements[temp_index])
            }
            $('#dragger-agent').children().remove();
            $('#dragger-agent').append(temp);
            $scope.a_rm_el_index = undefined;
          }else if(($scope.a_rm_el_index != undefined && $scope.a_rm_el_index === 0) || $scope.a_size !== al){
            var i = $scope.rem_agents.indexOf(new_agent);
            $scope.rem_agents.splice(i, 1);
            $scope.rem_agents.push($scope.a_rm_el_data);
            var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll'>\
                        <p style='margin-top:10px;text-align:center;'>"+new_agent+"</p>\
                    </div>";
            $(el).prependTo('#dragger-agent');
            $scope.a_rm_el_index = undefined;
        }else if($scope.a_rm_el_index != undefined && al !== $scope.agent_config_value){
          var i = $scope.rem_agents.indexOf(new_agent);
          $scope.rem_agents.splice(i, 1);
          var el = "<div class='w3-panel w3-card ng-scope' ng-repeat='item in $ctrl.agent_data' style='margin-top: -10px; cursor:all-scroll'>\
                        <p style='margin-top:10px;text-align:center;'>"+new_agent+"</p>\
                    </div>";
            $(el).prependTo('#dragger-agent');
            $scope.a_rm_el_index = undefined;
        }
      }
    }

    $scope.formData = function(){
            $scope.audit_per = document.getElementById('audit').value;
            $scope.random_per = document.getElementById('randomsample').value;
            if( $scope.audit_per !== "" || $scope.random_per !== ""){
              var packets = $('#dragger-packet').children();
              var agents = $('#dragger-agent').children();
              var total_packets = $('#dragger-packet').children().length;
              var total_agents = $('#dragger-agent').children().length;
              var packets_data = new Array(total_packets);
              var agents_data = new Array(total_agents);

              for(var i = 0; i<total_packets; i++)
                  packets_data[i] = packets[i].firstChild.nextElementSibling.innerText;

              for(var j = 0; j<total_agents; j++)
                  agents_data[j] = agents[j].firstChild.nextElementSibling.innerText;

              var center = $scope.sa_url_split[2].split('=')[1]
              var project = $scope.sa_url_split[1].split('=')[1]
              project = project.replace(/%20/g, ' ');
              var url = "/api/packet_agent_audit_random/";
              var data = {'packets':packets_data, 'agents':agents_data, 'audit':$scope.audit_per, 'random':$scope.random_per, 'from':$scope.start_date, 'to':$scope.end_date, 'project':project, 'center':center};


              $http({method:'POST', url:url, data:data, headers:{'Content-Type':'application/x-www-form-urlencoded;charset=utf-8;'}}).then(function(result){
                  if(typeof(result.data.audit) === "string" & typeof(result.data.random) === "string"){
                    swal({
                      title:'warning',
                      text:'Please select packets or agents to meet the intelligent audit criteria, and select high random value',
                      icon:'warning',
                      button:'ok'
                    });
                  }else if(typeof(result.data.audit) === "string"){
                    swal({
                      title:'warning',
                      text:'Please select the packets or agents to meet the criteria.',
                      icon:'warning',
                      button:'ok'
                    });
                  }else if(typeof(result.data.random) === "string"){
                    swal({
                      title:'warning',
                      text:'Please select the high random value.',
                      icon:'warning',
                      button:'ok'
                    });
                  }else{
                    $scope.success = true;
                    $scope.excel_data = result.data;
                  }
              });
            }else{
              swal({
                      title:'error',
                      text:'Please select intelligent audit or random audit.',
                      icon:'error',
                      button:'ok'
                    });
            }
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

    $scope.show_ok_audit = function(){
        var iav = $scope.intelligent_audit_value;
        if(iav === null){
          $scope.audit_value = null;
          $('.handle-audit').fadeOut(300);
          $('.audit-show').hide();
        }else{
          $('.handle-audit').fadeIn(300);
        }
    };

    $scope.show_ok_random = function(){
      var rav = $scope.random_audit_value;
        if(rav === null){
          $scope.random_value = null;
          $('.handle-random').fadeOut(300);
          $('.random-show').hide();
        }else{
          $('.handle-random').fadeIn(300);
        }
    }

    $scope.audit_submit = function(){
      $('.handle-audit').fadeOut(300);
      var audit_url = '/api/intelligent-audit/?audit_val='+$scope.intelligent_audit_value+'&total_production='+$scope.total_production;
      $http({method:'GET', url:audit_url}).then(function(result){
        $('.audit-show').show();
        $scope.audit_value = result.data;
      }, function(error){
        $scope.intelligent_audit_err_msg = true;
        console.log('something went wrong!');
      });
    };

    $scope.random_submit = function(){
      $('.handle-random').fadeOut(300);
      var random_url = '/api/random-audit/?random_val='+$scope.random_audit_value+'&total_production='+$scope.total_production;
      $http({method:'GET', url:random_url}).then(function(result){
         $('.random-show').show();
        $scope.random_value = result.data;
      }, function(error){
          $scope.random_audit_err_msg = true;
          console.log('something went wrong!');
      });
    }
});
