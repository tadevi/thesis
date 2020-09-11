camera_page = {
  cameras:new Map(),
  currentCameraId:-1,
  init:function() {
      $.ajax({
          type: "GET",
          url: "/cameras",
          success: function(data){
            console.log(data);
            camera_page.addCameras(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

        camera_page.socket = io.connect('/');

        camera_page.socket.on('connect', function() {
            camera_page.socket.emit('my event', {data: 'I\'m connected!'});
        });

        camera_page.socket.on('new camera', function(data) {
            camera_page.addCameras([data]);
        });
    },

    addCameras:function (data) {
        $.each(data, function(idx, camera) {
            var cameraId =  camera['camera_id'];

            var onClick = `camera_page.setCurrentCamera(${cameraId})`

            $('#cameraList').append(`
                <div>
                  <button class="btn btn-primary btn-block" onclick=${onClick}>Camera${cameraId}</button>
                </div>
            `);

            camera_page.cameras.set(cameraId, camera)
        });

        $('#noCamLabel').css('display', camera_page.cameras.size==0?'block':'none')

        if(camera_page.cameras.size>0 && camera_page.currentCameraId==-1){
            camera_page.setCurrentCamera(camera_page.cameras.keys().next().value)
        }
    },

    setCurrentCamera:function(cameraId){
        camera = camera_page.cameras.get(cameraId.toString())
        $('#cameraDetail').css('display', 'block')
        $('#cameraDesc').text(`Recorded violations of Camera${camera['camera_id']} at ${camera['location']}`)
        $('#violationTableBody').empty();
        $.ajax({
          type: "GET",
          url: "/violation",
          data: {
            camera_id: camera['camera_id']
          },
          success: function(data){
            console.log(data);
            camera_page.addNewViolations(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

        if(camera_page.currentCameraId>=0){
            camera_page.socket.off(`violation/cam${camera_page.currentCameraId}`);
        }

        camera_page.currentCameraId = camera['camera_id']

        camera_page.socket.on(`violation/cam${camera_page.currentCameraId}`, function(data) {
            camera_page.addNewViolations([data]);
        });
    },

    addNewViolations:function(violations){
        $.each(violations.reverse(), function(idx, violation){
            var newDate = new Date();
            newDate.setTime(violation['timestamp']);
            var formatted_timestamp = newDate.toUTCString();

            var formatted_record = `<tr>
                 <td>${formatted_timestamp}</td>
                 <td>${violation['type']}</td>
                 <td class="text-right"><img src=${violation['evidence']}
                 height="200"></img></td>
             </tr>`;

            if($("#violationTableBody tr").length>=19){
                $("#violationTableBody tr").last().remove();
            }

            $('#violationTable').prepend(formatted_record)
        })
    }
}