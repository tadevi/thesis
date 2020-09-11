air_page = {
  locations:[],
  currentLocationIdx:-1,
  init:function() {
      $.ajax({
          type: "GET",
          url: "/iot_locations",
          success: function(data){
            console.log(data);
            air_page.addLocations(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

        air_page.socket = io.connect('/');
    },

    addLocations:function (data) {
        $.each(data, function(idx, location) {
            var onClick = `air_page.setCurrentLocation(${idx})`

            $('#locationList').append(`
                <div>
                  <button class="btn btn-primary btn-block" onclick=${onClick}>${location}</button>
                </div>
            `);

            air_page.locations.push(location)
        });

        $('#noLocationLabel').css('display', air_page.locations.length==0?'block':'none')

        if(air_page.locations.length>0 && air_page.currentLocationIdx==-1){
            air_page.setCurrentLocation(0)
        }
    },

    setCurrentLocation:function(idx){
        var location = air_page.locations[idx]
        $('#locationDetail').css('display', 'block')
        $('#locationDesc').text(`Recorded Air Quality Data in ${location}`)
        $('#airTableBody').empty();
        $.ajax({
          type: "GET",
          url: "/iot/",
          data: {
            name: 'air',
            district: location
          },
          success: function(data){
            console.log(data);
            air_page.addNewAirRecords(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

        if(air_page.currentLocationIdx!=-1){
            air_page.socket.off(`iot/air/${air_page.locations[air_page.currentLocationIdx]}`);
        }

        air_page.currentLocationIdx = idx

        air_page.socket.on(`iot/air/${air_page.locations[air_page.currentLocationIdx]}`, function(data) {
            air_page.addNewAirRecords([data]);
        });
    },

    addNewAirRecords:function(data){
        var $el = $("#airTableBody");
//        $el.empty(); // remove old options
        $.each(data.reverse(), function(idx, record) {
            var newDate = new Date();
            newDate.setTime(record['timestamp']);
            var formatted_timestamp = newDate.toUTCString();
            var color
            var eval
            if(record['pm25']<50){
                color = "#3d9c09"
                eval = "Good"
            }else if(record['pm25']<100){
                color = "#d9bb36"
                eval = "Medium"
            }else if(record['pm25']<150){
                color = "#ff8000"
                eval = "Unhealthy"
            }else if(record['pm25']<200){
                color = "#e33232"
                eval = "Harmful"
            }else if(record['pm25']<300){
                color = "#5a0691"
                eval = "Very harmful"
            }else{
                color = "#590404"
                eval = "Dangerous"
            }

            var formatted_record = `<tr>
                     <td><font color=${color}>${record['device_id']}</font></td>
                     <td><font color=${color}>${record['location']}</font></td>
                     <td><font color=${color}>${formatted_timestamp}</font></td>
                     <td><font color=${color}>${record['pm25']}</font></td>
                     <td class="text-right"><font color=${color}><b>${eval}</b></font></td>
                     </tr>`;
          if($("#airTableBody tr").length>=19){
            $("#airTableBody tr").last().remove();
          }
          $el.prepend(formatted_record)
        });
    }
}