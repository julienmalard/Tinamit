.. _IPA:

IPA
===
El IPA (interfaz de programación de aplicaciones) permite conectar modelos de manera rápida, flexible, y reproducible. Tiene
las mismas funciones que el IGU, pero por ser una librería Python ya puedes automatizar el proceso. Si prefieres escribir 
líneas de código a hacer clic en botones, el IPA es para ti.

Preparar todo
-------------
Antes que todo, hay que importar los objetos de Tinamït que vamos a necesitar::

  from Conectado import Conectado

Esta línea importa la clase Conectado del módulo Conectado de Tinamït. Increíblemente, es la única cosa que tenemos que importar.

Cargar modelos
--------------
Primero, vamos a empezar por crear una instancia de la clase Conectado. Si no sabes lo que es una instancia de una clase, o 
puedes simplemente copiar el texto abajo, o (mejor) puedes echarle otro vistazo a tu último curso en Python. ::

  modelo = Conectado()

¿Pero cómo especificamos cuáles modelos biofísico y DS querremos? Esto se hace en la línea siguiente::

  modelo.estab_mds("C:\\Yo\\MisArchivos\\MiModeloVensim.vpm")

:func:`~tinamit.Conectado.Conectado.estab_mds`, como probablemente adivinaste, establece el modelo DS. Le tienes que
dar como argumento la ubicación del archivo ``.vpm`` de tu modelo DS publicado por Vensim. En el futuro, si Tinamït
puede aceptar modelos de otros programas que Vensim, podrás poner otros tipos de archivos aquí.

Y, para el modelo biofísico, especificamos la ubicación de la envoltura específica para el modelo biofísico que querremos usar. 
En este caso, vamos a usar SAHYSMOD, un modelo de flujos de agua subterránea y de salinidad. Esto no cambia mucho; cada vez que 
quieres conectar un modelo DS con un modelo en SAHYSMOD darás la misma envoltura, no importe cuáles variables estás conectando.::

  modelo.estab_bf(os.path.join(os.path.split(__file__)[0], 'mi_envoltura.py'))

(No te preocupes por lo del ``os.path.split(__file__)[0]``, es simplemente una manera en Python de obtener la dirección en tu 
computadora del directorio actual. Esto le permite al programa encontrar la envoltura para el modelo biofísico, no 
importe dónde lo guardará alguién en su computadora)

Conectar Variables
------------------
Ahora, vamos a conectar los dos modelos por crear enlaces entre los variables de cada uno. Cada conexión entre dos variables 
necesita 3 cosas: los nombres de los dos variables para conectar y la dirección de la conexión (es dec
ir, de cuál modelo sacas el valor del variable para ponerlo en el otro modelo). Una simulación verdaderamente dinámica incluirá 
conexiones en ambas direcciones (del modelo DS al biofísico y viceversa).::

  modelo.conectar(var_mds='Salinidad', mds_fuente=False, var_bf="Cr4 - Salinidad")
  
``var_mds`` es el nombre del variable en el modelo DS, y ``var_bf`` es el nombre del variable en el modelo biofísico (tal como 
especificado en la envoltura). ``mds_fuente`` indica si se lee el valor del variable en el modelo DS para transferirla al
modelo biofísico, o si es al revés. En este ejemplo, tomamos el valor de la salinidad del suelo del modelo SAHYSMOD
y lo pasamos al modelo DS (Vensim).

Opcionalmente, puedes especificar el parámetro ``conv``, un factor de conversión (si los dos variables tienen unidades 
distintas). Puedes conectar tantos variables como quieras. En nuestro ejemplo de SAHYSMOD que viene con Tinamït, conectamos un
total de 8 variables.

Simular
-------
Ya, por fin, podemos simular el modelo::

  modelo.simular(paso=1, tiempo_final=240, nombre_simul='Mi primera simulación Tinamït')
  
``paso`` indica el intervalo de tiempo al cual se intercambian valores de variables entre los dos modelos. ``tiempo_final`` 
indica la duración de la simulación, y ``nombre_simul`` es el nombre de la simulación que se dará al archivo con los egresos 
(resultados) de la simulación.

Implementación de políticas
---------------------------
Los que conocen los modelos de dinámicas de los sistemas sabrán que muchas veces se incorporan opciones de acciones o de 
políticas en los modelos con un variable “sí o no.” Por ejemplo, en nuestro modelo de salinidad de los suelos tenemos un 
variable llamado “Política de recuperación de aguas.” Si este variable es igual a 1, activará la parte del modelo de dinámicas 
de los sistemas para una política de recuperación de aguas. Si es igual a 0, no habrá intervención en la simulación. Estas 
cosas son muy útiles para comprobar la eficacidad (o no) de varias ideas de intervenciones en el sistema.

El asunto es que nosotros nos aburrimos muy rápido de tener que cambiar los valores de estos variables en el modelo Vensim y
tener que volver a publicarlo cada vez que querríamos analizar una combinación diferente de políticas. Con 5 posibilidades de 
políticas distintas en nuestro modelo ejemplo, ¡acabamos con muchas combinaciones y permutaciones!

Así que no se preocupen, ya incluimos una función en el IPA que les permite activar o desactivar una política en particular si 
tener que abrir Vensim y republicar el modelo para cada cambio. Actualmente, puedes emplear esta función para cambiar el valor
de cualquier variable en el modelo antes de empezar la simulación, pero es más útil que todo para activar y desactivar 
políticas. (¡Cuidado! Esta función solamente cambia el valor inicial del variable.)::

  modelo.mds.inic_val_var(var=”Política maravillosa”, val=1)
  
``modelo.mds`` accede el objeto de modelo DS asociado con el modelo conectado, y la función
:func:`~tinamit.Modelo.Modelo.inic_val_var`` hace exactamente lo que piensas que hace.

Resumen
-------
Y bueno, allí está. Ya puedes conectar, desconectar, simular y manipular modelos. Mira el documento “Ejemplo SAHYSMOD” en el 
directorio de ejemplos de Tinamït para un ejemplo del uso del IPA en la automatización de corridas para simular, de una vez, 5
corridas de un modelo socioeconómico DS con un modelo biofísico de calidad y salinidad de los suelos (SAHYSMOD).

Para las que conocen las funciones :py:mod:`threading` de Python, y que piensan que sería una manera brillante de correr las 
5 simulaciones en paralelo para ahorrar tiempo, no lo hagan. Pensamos lo mismo y cuando lo intentamos sucede que el DLL de 
Vensim no puede correr más que un modelo al mismo tiempo y se pone en un gran lío. Si no tienes ni idea de lo que estoy
diciendo, perfecto.
