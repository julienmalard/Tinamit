Introducción
============

¿Qué?
-----
En breve, Tinamït sirve para conectar modelos de dinámicas de los sistemas (DS) con modelos biofísicos. Permite el
intercambio de valores de variables entre ambos modelos (y en ambas direcciones) a cada paso de simulación, y eso, con
un mínimo de código (o, si de verdad lo quiere así, sin código cualquier).

¿Por qué?
---------
¿Por qué darse una tal tarea? Bueno, querer conectar modelos es algo bastante común. En nuestro caso,  los modelos DS
son excelentes para involucrar a actores claves en el desarrollo del modelo, porque son visuales e intuitivos
(al menos, tanto como lo puede ser un modelo). Si uno está, por ejemplo, construyendo un modelo del sistema humano
(socioeconómico) de agricultores con problemas de degradación de suelos, un modelo DS sería perfecto para involucrar
a agricultores, investigadores, agentes del gobierno, y otros en la construcción del modelo socioeconómico.

Pero son bastante inútiles para representar procesos físicos más complejos, como el flujo de agua y de sal que resulta
en la degradación del suelo. Esto es problemático, porque la relación entre humanos y ambiente es recíproca, y para
obtener resultados interesantes tenemos que incluir los dos y sus interacciones. Por ejemplo, la calidad del suelo y
el rendimiento agrícola determinará el ingreso de agricultores, lo cual en su turno determinará las prácticas de
gestión de los suelos que adoptan.

Y sí, por supuesto que ya existen muchas maneras de conectar estos tipos de modelos. Pero la mayoría involucra cientos
de líneas de código, que usted tendrá que entender (incluso, por ejemplo, el manejo del DLL de Vensim y de la línea de
comanda), y, si jamás decide uno hacia cambiar el nombre de un variable o conectar un variable más (o menos), habrá
que volver a meterse de nuevo a descifrar todo el código. Lo que no es un punto favorable cuando quieres convencer
una profesional en, digamos, agricultura o política que el modelo que vas a construir con ella será muy fácil
utilizar después de que te vayas.

.. figure:: Imágenes/Estructura_concep.png
   :align: center
   :alt: Diagrama de la estructura conceptual de Tinamït.
   
   Figura 1

   Diagrama de la estructura conceptual de Tinamït.

Por eso se inventó Tinamït, el programa gratis y libre para hacer todo eso para ti. Viene con:

* Funciones predefinidas y flexibles para conectar modelos DS y biofísicos y simular el modelo conectado.
* Un interfaz gráfico de usuario (IGU) muy lindo, para los que le tienen miedo al código.
* Hablando del IGU, está disponible en varios idiomas, y siempre puedes agregarle una nueva y compartirla con
  quien quieras.

Con Tinamït, cambiar la conexión entre los modelos o lanzar una nueva simulación se hace con el pequeño cambio de una
línea de código o, en el interfaz, con un clic del ratón.

Lo único difícil es que, para cada tipo de modelo biofísico, hay que escribir un código (una “envoltura”) que pueda
llamar las funciones de simulación y de lectura y cambio de valores de variables en este modelo biofísico. Sí, es
trabajo para alguien a quien le gusta la programación, pero lo bueno es que una vez hecha para un tipo de modelo
biofísico ya no hay necesidad de volverlo a hacer, no importe con qué modelo lo vas a conectar. Tinamït ya
viene con envolturas para algunos modelos biofísicos, y seguirá agregando más en tanto los escriben sus usuarios
(¡ustedes!). Bueno, sabemos que no es ideal, pero es una limitación inevitable de conectar modelos (aunque no
usaras Tinamït, lo tendrías que hacer de todo modo). Y, de verdad, para todo lo bueno de Tinamït, es un asunto
de poca importancia.

En este manual, se supondrá que ya conoces, al menos, el siguiente:

* Modelos de dinámicas de los sistemas
* Modelos físicos (en general)
* Python

Si no es el caso, ahora sería un momento excelente para ir a estudiarlos un poco. (¿Sabías? Para Python,
`CodeCademy <www.codecademy.com>`_ tiene un curso fenomenal, gratis y en español.)
