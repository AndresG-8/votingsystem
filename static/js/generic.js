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

var csrftoken = getCookie('csrftoken');



$(document).ready(function() {

    document.getElementById('result_message').style.display = 'none';

    var contador = 1;
    $("#addProfileFormField").click(function() {
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
        var datos = new FormData();
        datos.append('program', $("#program").val())
        datos.append('profile_image', $("#profile_image")[0].files[0])

        $(".propossals").each(function(index) {
            datos.append('propossals' + index, $(this).val());
        });

        $.ajax({
            url: 'profile',
            type: "POST",
            data: datos,
            contentType: false,
            processData: false,
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response) {
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
  
// const toggleTheme = () => {
//   const theme = document.querySelector('[data-bs-theme-value]').dataset.bsThemeValue;
//   console.log("Color obtenido: "+theme);
//   // document.querySelector('html').classList.toggle('theme-' + theme);
//   document.documentElement.setAttribute('data-bs-theme', theme)
//   console.log("Cambiando color: "+theme);
// };
  
// document.querySelector('#light').addEventListener('click', toggleTheme);
// document.querySelector('#btn-dark').addEventListener('click', toggleTheme);

const toggleTheme = (event) => {
  const theme = event.target.dataset.bsThemeValue;
  console.log("Color obtenido: "+theme);
  document.documentElement.setAttribute('data-bs-theme', theme)
  console.log("Cambiando color: "+theme);
};
  
document.querySelector('#btn-light').addEventListener('click', toggleTheme);
document.querySelector('#btn-dark').addEventListener('click', toggleTheme);
