air_fog = {
    init:function() {
        var socket = io.connect('/');

        socket.on('connect', function() {
            socket.emit('my event', {data: 'I\'m connected!'});
        });

        socket.on('iot/air/Thu Duc', function(data) {
            air_fog.addNewRecords([data]);
        });
    },

    addNewRecords:function(data){
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