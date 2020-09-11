camera_fog = {
  cameras: [],

  init:function() {
      $.ajax({
          type: "GET",
          url: "/cameras",
          success: function(data){
            console.log(data);
            camera_fog.addCameras(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

        var socket = io.connect('/');

        socket.on('connect', function() {
            socket.emit('my event', {data: 'I\'m connected!'});
        });

        socket.on('new camera', function(data) {
            camera_fog.addCameras([data]);
        });
    },

    addCameras:function (data) {
        $.each(data, function(idx, camera) {
          var cameraId =  "cameraView" + idx;
          $('#cameraGrid').append(`<div class="grid-item">
            <label for=${cameraId}>Camera ${camera['camera_id']}</label>
            <img id=${cameraId} style="-webkit-user-select: none;margin: auto;" src=${camera['url']} onerror="camera_fog.reloadCameraStream(this);">
          </div>`);
        });

        camera_fog.cameras = camera_fog.cameras.concat(data)
        $('#noCamLabel').css('display', camera_fog.cameras.length==0?'block':'none')
    },

    reloadCameraStream:function (image) {
        var temp = image.src
        image.src = "/static/assets/img/blank.jpg"
        setTimeout(function() {
            console.log(`reload stream ${image.src}`)
            image.src = temp
        }, 1000);
    }
}