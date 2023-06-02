# votingsystem
# Sistema de Votaciones basado en Blockchain

Este proyecto implementa un Sistema de Votaciones seguro y transparente que utiliza tecnología Blockchain para garantizar 
la integridad y trazabilidad de los votos. La aplicación está diseñada para evitar el fraude y proporcionar un registro de 
votación verificable, haciendo que cada voto cuente.

## Tecnología

El sistema está programado en Python utilizando el popular framework web Django. Django fue seleccionado por su capacidad
para manejar aplicaciones web complejas y su robusta seguridad. A su vez, este proyecto hace uso de varias librerías notables 
como:

- `django.contrib.auth`: Para el manejo de la autenticación de usuarios.
- `Crypto.Cipher.PKCS1_OAEP`: Usado para la encriptación y desencriptación de datos, garantizando la seguridad de las votaciones.
- `django.contrib.messages`: Para la manipulación de mensajes flash, permitiendo una interacción fluida con el usuario.
- entre otras.

Este sistema de votación basado en Blockchain combina estas tecnologías para ofrecer una solución sólida y segura a los desafíos 
de la votación en línea.

## Instrucciones de descarga: Github ofrece una variedad de opciones de descarga. 

Ingresando a la siguiente URL: https://github.com/AndresG-8/votingsystem, buscar el botón de “<> Code” y proceder a clonar el 
repositorio usando git, abriéndolo directamente en Visual Studio Code o descargándolo como zip. 
Instrucciones de instalación: Para esta instalación, se ha de usar la opción de clonar el repositorio usando Git (Git bash, 
la consola de git), para esto se usa la siguiente URL (https://github.com/AndresG-8/votingsystem.git) y se siguen los pasos descritos a 
continuación: 

```git
git clone https://github.com/AndresG-8/votingsystem.git
cd votingsystem/
```

Una vez se ha descargado el proyecto, se debe iniciar un entorno virtual, en este caso, se creará usando “Virtual Env”, la cual es una 
librería de Python para este tema, desde allí se hará el despliegue de la aplicación. Para esto, abrir el “Command Prompt” o “CMD” y 
también conocida como terminal de Windows, se debe navegar hasta la carpeta donde se descargó el proyecto, en este caso: votingsystem/. 
Ingresar allí los siguientes comandos:

```git
pip install virtualenv
virtualenv -p python3 venv
.\venv\Scripts\activate
python manage.py runserver
```

Ahora, se ingresa desde cualquier navegador a la url arrojada por el último comando, que suele ser http://127.0.0.1:8000/

## Contribución

Las contribuciones son bienvenidas. Por favor, lee las [directrices de contribución](CONTRIBUTING.md) para más información.
