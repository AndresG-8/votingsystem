/*** javascript general, ajax */
// $(document).ready(function(){

//     $('#btnSaveCuenta').click(function(){
//         var serializeData = $('#cuentaForm').serialize();
//         // console.log(serializeData)

//         $.ajax({
//             url: $('#cuentaForm').data('url'),
//             data: serializeData,
//             type: 'POST',
//             success: function(response) {
//                 $('#cuentaList').append('<div class="card  card-body"><p><strong>' + response.cuenta.nombre_cuenta + '</strong> - ' + response.cuenta.comentarios + ' - ' + response.cuenta.saldo_inicial + '</p></div>')
//             }
//         })

//         $('#cuentaForm')[0].reset();
//     });
// });

var csrftoken = getCookie('csrftoken');

$(document).ready(function() {

    document.getElementById('result_message').style.display = 'none';

    var contador = 1;
    $("#addProfileFormField").click(function() {
        // contador++;
        $("#inputContainer").append('<div class="mb-3"><div class="input-group"><input type="text" name="propossals" class="propossals form-control" placeholder="Ingrese propuesta"><button type="button" class="remove btn btn-danger">X</button></div></div>');
    });

    $('#inputContainer').on('click', '.remove', function() {
        $(this).closest('.input-group').remove();
        $("#result_message").html("Recuerda guardar los cambios con el botón de Actualizar perfil"); 
        document.getElementById('result_message').style.display = 'block';
        setTimeout(function() {
            document.getElementById('result_message').style.display = 'none';
        }, 2000);  
    });   

    $("#updateProfileForm").on("submit", function(e) {
        e.preventDefault();
        // var datos = {};
        // datos['program'] = $("#program").val();
        // datos['profile_image'] = $("#profile_image").val();
        var datos = new FormData();
        datos.append('program', $("#program").val())
        datos.append('profile_image', $("#profile_image")[0].files[0])

        $(".propossals").each(function(index) {
            datos.append('propossals' + index, $(this).val());
            // console.log('contador:' + contador)
            // datos['propossals' + contador] = $(this).val();
            // contador++;
        });

        $.ajax({
            url: 'profile',
            type: "POST",
            data: datos,
            // data: JSON.stringify(datos),
            // contentType: "application/json",
            contentType: false,
            processData: false,
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response) {
                // Aquí puedes hacer algo con la respuesta del servidor, si lo necesitas.
                // console.log(response);  // Imprime la respuesta del servidor en la consola
                // console.log(response['new_image'])
                
                // var listItems = "";
                // $.each(datos, function(key, value) {
                //     if(key.includes('propossals')){
                //         listItems += "<li>" + value + "</li>";
                //     }
                // });
                // $("#new_proposals").html(listItems); 
                var listItems = "";
                for (var pair of datos.entries()) {
                    var key = pair[0];
                    var value = pair[1];
                    if(key.includes('propossals')){
                        listItems += "<li>" + value + "</li>";
                    }
                }
                $("#new_proposals").html(listItems);

                $("#new_image").html('<p><img src="/media/'+response['new_image']+'" alt="Profile image" heigth="150px" width="150px"></p>');

                $("#result_message").html("La operación fue exitosa!"); 
                document.getElementById('result_message').style.display = 'block';
                setTimeout(function() {
                    document.getElementById('result_message').style.display = 'none';
                }, 5000);     

            }
        });
    });

});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// $(document).ready(function() {
//     $('#addProfileFormField').on('click', function() {
//         var newInput = $('<input type="text" name="propossals" id="propossals" class="form-control" placeholder="Ingrese propuesta">');
//         $('.inputContainer').append(newInput);
//     });
// });

