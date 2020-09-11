device_page = {
  records:[],
  init:function() {
      $.ajax({
          type: "GET",
          url: "/devices",
          success: function(data){
            device_page.addNewRecords(data['data']);
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
         }
        });
    },

    addNewRecords:function(data){
        var $el = $("#tableBody");
        $.each(data, function(idx, record) {
            var onClick = `device_page.startDevice(${idx})`

            var formatted_record = `<tr>
                 <td>${record['device_id']}</td>
                 <td>${record['type']}</td>
                 <td>${record['location']}</td>
                 <td class="text-right">
                    <div>
                      <button class="btn btn-primary btn-block" onclick=${onClick}>START</button>
                    </div>
                 </td>
             </tr>`;

          $el.append(formatted_record)
        });
        device_page.records = data
    },

    startDevice:function(idx){
        record = device_page.records[idx]
        console.log(record['post_data'])
        $.ajax({
          type: "POST",
          url: record['post_url'],
          contentType: 'application/json',
          data: JSON.stringify(record['post_data']),
          success: function(data){
            console.log('success')
          },
          error: function(xhr, error){
            console.log("fail with status: "+xhr.status+", text: "+xhr.responseText)
          }
        });
    }
}