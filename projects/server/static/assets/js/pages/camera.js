camera = {
  loadAllCamera:function() {
      $.ajax({
          type: "GET",
          url: "/camera",
          success: function(data){
            console.log(data);
            camera.updateCameraList(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

      $('#cameraSelect').on('change', function() {
           $('#cameraView').attr('src', this.value);
           console.log('change src to '+this.value);
      });
    },

    updateCameraList:function(data){
        var $el = $("#cameraSelect");
        $el.empty(); // remove old options
        $.each(data, function(idx, camera) {
            console.log(camera)
          $el.append($("<option></option>")
             .attr("value", camera['url']).text("Cam"+camera['camera_id']));
        });
        cameras = data;
        if(cameras.length>0){
            $el.val(cameras[0]['url']).change();
        }
    }
}