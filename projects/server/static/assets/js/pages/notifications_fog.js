notifications_fog = {
    init:function(){
        $.ajax({
          type: "GET",
          url: "/notifications",
          success: function(data){
            notifications_fog.addNewNotifications(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });

        var socket = io.connect('/');

        socket.on('connect', function() {
            socket.emit('my event', {data: 'I\'m connected!'});
        });

        socket.on('notification/Thu Duc', function(notification) {
            notifications_fog.addNewNotifications([notification]);
        });
    },

    addNewNotifications: function(notifications){
        var $el = $("#notiList");

        $.each(notifications.reverse(), function(idx, notification) {
            if($el.length>=19){
                $el.last().remove();
            }

            $el.prepend(`
                <div class="alert alert-${notification['type']}">
                  <span>
                    ${notification['message']}
                  </span>
                </div>
            `)
        })
    }
}