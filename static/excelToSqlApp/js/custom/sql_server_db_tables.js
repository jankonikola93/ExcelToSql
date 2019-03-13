$().ready(function(){
    frmCreateTableSubmit();
    frmUpdateTableSubmit();
})

function frmCreateTableSubmit(){
    $('#frm_create_table').on('submit', function (event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: new FormData(this),
            processData: false,
            contentType: false,
            //dataType: "dataType",
            success: function (data) {
                if(data.hasErrors){
                    alertBox(true, data.errors)
                }
                else if(data.success){
                    alertBox(false, data.messages);
                }
                else{
                    $('#panel_create_table').html(data);
                    frmCreateTableSubmit();
                }
            },
            error: function(error){
                alertBox(true, 'Error in comunication with server');
            }
        });
    });
}

function frmUpdateTableSubmit(){
    $('#frm_update_table').on('submit', function (event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: "data",
            data: new FormData(this),
            processData: false,
            contentType: false,
            //dataType: "dataType",
            success: function (data) {
                if(data.hasErrors){
                    alertBox(true, data.errors)
                }
                else if(data.success){
                    alertBox(false, data.messages);
                }
                else{
                    $('#panel_update_table').html(data);
                    frmUpdateTableSubmit();
                }
            },
            error: function(error){
                alertBox(true, 'Error in comunication with server');
            }
        });
    });
}

function alertBox(isError, text) {
    if (isError) {
        $('#modal_alert_text').html(text);
        $('#modal_alert_content').addClass('bg-danger');
        $('#modal_alert_content').removeClass('bg-success');
        $('#modal_alert').modal("show");
    } 
    else {
        $('#modal_alert_text').html(text);
        $('#modal_alert_content').addClass('bg-success');
        $('#modal_alert_content').removeClass('bg-danger');
        $('#modal_alert').modal("show");
    }
}