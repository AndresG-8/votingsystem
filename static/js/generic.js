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
  
// const toggleTheme = (event) => {
//   const theme = event.target.dataset.bsThemeValue;
//   console.log("Color obtenido: "+theme);
//   document.documentElement.setAttribute('data-bs-theme', theme)
//   console.log("Cambiando color: "+theme);
// };
  
// document.querySelector('#btn-light').addEventListener('click', toggleTheme);
// document.querySelector('#btn-dark').addEventListener('click', toggleTheme);

(() => {
    'use strict'

    const storedTheme = localStorage.getItem('theme')
    
    const getPreferredTheme = () => {
        if (storedTheme){
            return storedTheme
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const setTheme = function (theme) {
        if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-bs-theme', 'dark')
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme)
        }
        localStorage.setItem('theme', theme)
    }

    setTheme(getPreferredTheme())

    $('#change-theme').on('click', '#btn-dark', function() {
        setTheme('dark')
    });
    
    $('#change-theme').on('click', '#btn-light', function() {
        setTheme('light')
    });

    window.addEventListener('DOMContentLoaded', () => {
        document.querySelector('#btn-dark').addEventListener('click', setTheme(getPreferredTheme()));
        document.querySelector('#btn-light').addEventListener('click', setTheme(getPreferredTheme()));
    })
})()

// JavaScript de Bootstrap (de la página oficial) que se utiliza para cambiar el tema de una página web entre "claro" y "oscuro",
// y para recordar la preferencia del usuario utilizando el almacenamiento local del navegador.

// // 1. `(() => { ... })()`: Esta es una función de flecha inmediatamente invocada (IIFE, por sus siglas en inglés). 
// // Se utiliza para crear un nuevo ámbito de variables y evitar la contaminación del ámbito global.
// (() => {
//     // 2. `'use strict'`: Esta línea activa el modo estricto en JavaScript, lo que hace que el código sea más seguro al prevenir 
//     // ciertas acciones y arrojar más excepciones.
//     'use strict'

//     // 3. `const storedTheme = localStorage.getItem('theme')`: Esta línea obtiene el tema almacenado en el almacenamiento local 
//     // del navegador, si existe.
//     const storedTheme = localStorage.getItem('theme')

//     // 4. `getPreferredTheme`: Esta función devuelve el tema preferido del usuario. Si el usuario ha seleccionado un tema antes, 
//     // lo obtiene del almacenamiento local. Si no, verifica si el usuario prefiere el tema oscuro utilizando la consulta de medios 
//     // `prefers-color-scheme`.
//     const getPreferredTheme = () => {
//       if (storedTheme) {
//         return storedTheme
//       }
  
//       return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
//     }

//     // 5. `setTheme`: Esta función establece el tema de la página web. Si el tema es 'auto', verifica si el usuario prefiere el 
//     // tema oscuro. Si es así, establece el tema oscuro. Si no, establece el tema que se le pasó a la función.
//     const setTheme = function (theme) {
//       if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
//         document.documentElement.setAttribute('data-bs-theme', 'dark')
//       } else {
//         document.documentElement.setAttribute('data-bs-theme', theme)
//       }
//     }
  
//     setTheme(getPreferredTheme())

//     // 6. `showActiveTheme`: Esta función actualiza la interfaz de usuario para mostrar el tema activo. Cambia el icono del tema, 
//     // el texto y el estado de los botones de cambio de tema.
//     const showActiveTheme = (theme, focus = false) => {
//       const themeSwitcher = document.querySelector('#bd-theme')
  
//       if (!themeSwitcher) {
//         return
//       }
  
//       const themeSwitcherText = document.querySelector('#bd-theme-text')
//       const activeThemeIcon = document.querySelector('.theme-icon-active use')
//       const btnToActive = document.querySelector(`[data-bs-theme-value="${theme}"]`)
//       const svgOfActiveBtn = btnToActive.querySelector('svg use').getAttribute('href')
  
//       document.querySelectorAll('[data-bs-theme-value]').forEach(element => {
//         element.classList.remove('active')
//         element.setAttribute('aria-pressed', 'false')
//       })
  
//       btnToActive.classList.add('active')
//       btnToActive.setAttribute('aria-pressed', 'true')
//       activeThemeIcon.setAttribute('href', svgOfActiveBtn)
//       const themeSwitcherLabel = `${themeSwitcherText.textContent} (${btnToActive.dataset.bsThemeValue})`
//       themeSwitcher.setAttribute('aria-label', themeSwitcherLabel)
  
//       if (focus) {
//         themeSwitcher.focus()
//       }
//     }
  
//     // 7. `window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', ...)`: Este código agrega un oyente de eventos 
//     // que se activa cuando cambia la preferencia de color del sistema del usuario. Si el usuario no ha seleccionado explícitamente un tema
//     // claro u oscuro, cambia el tema de la página web para que coincida con la preferencia del sistema.
//     window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
//       if (storedTheme !== 'light' || storedTheme !== 'dark') {
//         setTheme(getPreferredTheme())
//       }
//     })
  
//     // 8. `window.addEventListener('DOMContentLoaded', ...)`: Este código agrega un oyente de eventos que se activa cuando se ha cargado 
//     // el contenido de la página web. Agrega oyentes de eventos a los botones de cambio de tema para que, cuando se haga clic en uno, 
//     // cambie el tema de la página web, lo guarde en el almacenamiento local y actualice la interfaz de usuario para mostrar el tema activo.
//     window.addEventListener('DOMContentLoaded', () => {
//       showActiveTheme(getPreferredTheme())
  
//       document.querySelectorAll('[data-bs-theme-value]')
//         .forEach(toggle => {
//           toggle.addEventListener('click', () => {
//             const theme = toggle.getAttribute('data-bs-theme-value')
//             localStorage.setItem('theme', theme)
//             setTheme(theme)
//             showActiveTheme(theme, true)
//           })
//         })
//     })
//   })()



