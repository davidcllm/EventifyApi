Nota: Se recomienda ingresar al link del repositorio para seguir las instrucciones con mayor comodidad: https://github.com/davidcllm/EventifyApi.

Para la ejecución del proyecto, favor de descargar el .zip del proyecto, que se encuentra en la página principal de este repositorio dentro del botón verde "Code". Si no se enceuntra en el repositorio, puede ingresar
con la liga anterior. 
<img width="1137" height="666" alt="imagen" src="https://github.com/user-attachments/assets/f7a88108-e3b4-4b7a-84b6-9c8c1557a9d7" />

O, en caso de haber recibido el .zip directamente desde nosotros, omitir lo anterior. Nos vamos a las descargas, donde se encuentra el .zip, se hace click derecho sobre él y se selecciona la opción de "Extraer todo", 
saldrá una ventana llamada "Extraer carpetas comprimidas (en zip)", y damos click en "Extraer". Se ingresa en la primera carpeta que sale después de extraer, donde se encontrarán los siguientes archivos:
<img width="928" height="465" alt="imagen" src="https://github.com/user-attachments/assets/f6e19de2-2f8e-4fe7-a3bd-3bef36e2df7e" />

Como puede ver el proyecto usa docker, pero antes de ejecutar el comando de contrucción de los contenedores, se necesita crear un archivo en la raíz del proyecto, es decir, en la misma ruta de la imagen anterior. 
Dicho archivo, será el .env, el cual puede crear con el editor de código de su preferencia, aquí está un ejemplo de cómo tiene que ser dicho .env:
<img width="312" height="148" alt="imagen" src="https://github.com/user-attachments/assets/204f3c90-74bb-46f1-b577-3afc4e135c61" />

En "DB_PASSWORD" y "DB_NAME" puede poner los valores que guste, sin embargo, los otros tres tienen que venir tal cual como en la imagen. Una vez creado el .env en la raíz del proyecto, copiamos la ruta de la barra 
de navegación del explorador de archivos, nos vamos a la terminal e ingresamos "cd [rutaCopiada]" en mi caso es "C:\Users\davcm\Downloads\EventifyApi-master\EventifyApi-master". Al estar en la ruta, 
ejecutamos "docker compose up --build".  
<img width="1447" height="471" alt="imagen" src="https://github.com/user-attachments/assets/c2339d15-880e-4402-872b-7f3d35f09476" />

Si al terminar la ejecución le aparece un error similar a este:
<img width="1468" height="239" alt="imagen" src="https://github.com/user-attachments/assets/88c1171a-e2fd-4b0c-88d1-f9e17bd23a60" />

Es probable que el puerto de la base de datos está ocupado, para solucionarlo abriremos el archivo "docker-compose.yml" con algún editor de código o el bloc de notas, haciendo click derecho sobre el archivo -> click 
en Abrir con -> click en Elegir otra aplicación -> selecciona el bloc de notas (o el edito de código de su preferencia). Al abrir el archivo, se busca el servcio "db" y en ese servicio busca la sección de ports. Por 
defecto vendrá el puerto "5432:5432", favor de cambiar esa parte por "5433:5433" o similar, guardar y salir del archivo.
<img width="741" height="553" alt="imagen" src="https://github.com/user-attachments/assets/7cbd15bd-12cb-44b3-90a1-020eedc48e7f" />

Otra opción para solucionarlo, es que se puede eliminar el contendor que esté ocupando el puerto en docker desktop: 
<img width="1580" height="882" alt="imagen" src="https://github.com/user-attachments/assets/9bd4053f-9f76-46b3-bd40-a02dc0507e75" />

Otro posible error, pero poco probable que suceda, es que se tenga un contenedor con el mismo nombre que alguno o varios de los nuestros, si es el caso, favor de eliminar los otros contenedores. Después de cambiar 
el puerto o eliminar el contenedor que esté ocupando ese puerto, ejcutamos el comando: "docker compose down -v", después de ello, volvemos a ejecutar "docker compose up --build" en la misma ruta del archivo extraído 
del .zip. Posteriormente, el contenedor de docker se habrá creado y podremos probar los distintos endpoints de la aplicación con Postman o la herramienta de su preferencia.
<br>
Si se siguieron estos pasos correctamente, la aplicación podrá ser usada. Para detener la ejecución, pulsar Ctrl+C en la terminal si es ejecución en primer plano, o ingresar el comando "docker compose stop" si se está 
ejecutando en segundo plano. Para ejecutar la aplicación en segundo plano el comando es "docker compose up -d", en primer plano "docker compose up". Para eliminar los contenedores se usa "docker compose down", si se 
desea eliminar los contenedores, redes y volúmenes de datos se ingresa "docker compose down -v". Todo esto también se puede hacer con el GUI de Docker Desktop, en la sección de "Contenedores". Para detener la 
aplicación está el ícono del cuadrado, para eliminar el contenedor está el botón rojo. Ambos señalados a continuación: 
<img width="1176" height="161" alt="imagen" src="https://github.com/user-attachments/assets/66403bc4-1fd9-4ace-9c57-9e7a615b8195" />


Para ejecutar la aplicación desde el GUI, se pulsa el botón de "Play" señalado a continuación: 
<img width="1180" height="164" alt="imagen" src="https://github.com/user-attachments/assets/c9124f90-37e0-49b6-a39b-32d72f2329c1" />



