Cómo se emplea Tinamit
======================

Hay dos maneras de usar Tinamit. Si quieres hacerlo sin código cualquier, el IGU (Interfaz de Usuario Gráfico) es para ti.
Si prefieres hacerlo con unas pocas líneas de código (lo cual puede acelerar bastante tu trabajo si tienes muchas simulaciones
diferentes que quieres automatizar), entonces el IPA (Interfaz de Programación de Aplicaciones) es la mejor opción.

Al final, el IGU y el IPA hacen el mismo trabajo (el IGU tiene botones muy lindos para llamar las funciones del IPA de manera
automática).

Preparación pre-uso
-------------------
No importe cuál del IPA o el IGU eliges usar, hay unas acciones preparatorias de las cuales no podrás escaparte.

Preparación del modelo DS
^^^^^^^^^^^^^^^^^^^^^^^^^
Tendrás que preparar el modelo de dinámicas de los sistemas antes de poder conectarlo. Para VENSIM (por el momento, Tinamit
funciona con VENSIM solamente), primero hay que ir a cada variable en tu modelo VENSIM que quieres que pueda recibir valores 
desde el modelo biofísico y escoger “Gaming” como tipo de variable. Después, hay que publicar el modelo en formato .vpm.

Preparación del modelo biofísico
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Si ya existe una envoltura específica para el modelo biofísico, no tienes que hacer nada más. Si no está disponible ya, tendrás
que escribir una (o convencer a alguien de hacerlo para ti). Otra parte de este manual (que todavía no he escrito) te explicará 
cómo hacer esto.

El IGU
------
Para los que no quieren programar, el IGU ofrece una manera sencilla de acceder (casi) todas las funcionalidades del IPA Tinamit,
y algunas adicionales.

Cambiar idiomas
^^^^^^^^^^^^^^^
Bueno, primero, de pronto no hables español. O posiblemente trabajas con gente que no lo habla, y quieres hacerles la cortesía 
de trabajar en su idioma. O tal vez quieres practicar un idioma que no has hablado por mucho tiempo.

Mientras que el código de Tinamit sí mismo es en español, el interfaz de Tinamit está disponible en muchos idiomas (y siempre 
puedes agregar un nuevo).

Para cambiar idiomas, hacer clic en el icono del :guilabel:`globo terrestre`.

En el centro, tienes las lenguas ya traducidas. Puedes escoger una con la cajita verde a la izquierda, o pulsar en lapicito 
para hacer cambios a la traducción.

A la izquierda, tienes lenguas en progreso. La barra muestra el estado del progreso de la traducción. Puedes escoger una como 
lengua de interfaz; las traducciones que faltan aparecerán como espacios vacíos. También puedes hacer clic en el lapicito para 
contribuir a la traducción.

Y, por fin, a la derecha tienes lenguas que todavía no hemos empezado a traducir. Puedes hacer clic en el lápiz para empezar 
la traducción. También puedes hacer clic en la cruz arriba para agregar un nuevo idioma que no se encuentra en la lista ya (y
también especificar si se escribe de la izquierda hacia la derecha o al revés).

Todas las traducciones se guardan automáticamente en un documento llamado “Trads” en el directorio de Tinamit. Si contribuyes
a unas traducciones, puedes compartir este documento (julien.malard@mail.mcgill.ca, o por GitHub) para que todas tengan acceso
a tu idioma favorito.

Cargar modelos (I)
^^^^^^^^^^^^^^^^^^
El flujo de trabajo en Tinamit tiene cuatro etapas (en números mayas) y el interfaz desbloquea el acceso a cada etapa en 
cuanto termines la etapa precedente.

La primera etapa sería, por supuesto de cargar los modelos biofísicos y DS.

Conectar modelos (II)
^^^^^^^^^^^^^^^^^^^^^
Después de eso, vamos a conectar los dos modelos por sus variables comunes. La flecha muestra la dirección de la conexión, y 
puedes especificar un factor de conversión, si quieres. Hay que hacer clic en “guardar” cada vez que haces una conexión.

Si haces un error, puedes volver a editar una conexión ya hecha por hacer clic en el lapicito verde, o simplemente borrarla 
con la cruz roja. Nota que el interfaz no te dejará conectar un variable más que una vez al mismo tiempo (eso sería una falla
lógica en la conexión de los dos modelos).

Simular (III)
^^^^^^^^^^^^^
Ya puedes simular los modelos conectados. Puedes especificar el paso y el tiempo final de la simulación. Finalmente, puedes 
especificar un factor de conversión entre el paso de cada modelo si los dos modelos no tienen las mismas unidades para sus 
pasos de tiempo (por ejemplo, si tu modelo DS funciona en meses y tu modelo biofísico en años, lo cual sería una situación 
muy común).

Incertidumbre (IV)
^^^^^^^^^^^^^^^^^^
Un día, en el futuro, Tinamit tendrá unas funciones de autocalibración y de análisis de incertidumbre. Entre tanto, la página
para esta cuarta etapa queda un blanco muy bonito.

Guardar y cargar modelos conectados
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^Ah, sí, ¿qué pasa si no terminas todo antes del almuerzo? No te preocupes, que no vas a perder todo. Allí, arriba por a la
izquierda del logo muy bonito de Tinamit, hay cuatro botones muy útiles. Uno guarda tu trabajo, uno lo guarda bajo un nuevo
nombre, otro abre un trabajo ya guardado y el último borra todo y te deja empezar de cero. No te voy a decir cuál es cuál.

El IPA
------








