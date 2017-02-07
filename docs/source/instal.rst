Instalación
===========

.. contents:: Contenido
   :depth: 3

Si sabes lo que estás haciendo
------------------------------
¡Felicitaciones! Tinamit necesita Python 3.5+, NumPy, SciPy, y Matplotlib. Tinamit sí mismo es un paquete de Python que se 
puede conseguir con

   :command:`pip install tinamit.`

Si no sabes lo que estás haciendo (para Windows)
------------------------------------------------
Esto es para Windows. Es un poco complicado, así que si tienes dificultades no dudes en pedirme ayuda 
(|correo|) para que te ahorres los dolores de cabeza que yo ya pasé.

Si estás usando Linux, no tengo idea cómo funciona pero me han dicho que es bastante más fácil que para los pobres que 
todavía seguimos con Windows.

Si estás usando un Mac, no tengo idea cómo funciona y parece bastante más difícil que para un Windows.

Instalación de Python
^^^^^^^^^^^^^^^^^^^^^
Primer que todo, hay que instalar Python. Puedes cargar la versión la más recién de aquí (https://www.python.org/downloads).

Instalación de paquetes adicionales
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
El problema con Python es que, mientras que es mucho más fácil para leer o escribir que otras lenguas (si no me crees, 
busca Fortran o C++), también es bastante más lento. Por eso, códigos Python que involucran muchos cálculos numéricos
se escriben con extensiones en Fortran o en C para aumentar la velocidad un poco. No te preocupes, ¡que Tinamit no tiene
nada en Fortran o C! Es puro Python. Pero desafortunadamente para sus funciones matemáticas necesita unos paquetes adicionales
de Python (NumPy, SciPy y Matplotlib), y ellos, sí tienen extensiones raras.

Si sabes cómo instalar estas y compilar código C directamente en tu computadora, perfecto. Si, como la mayoría de la
gente normal, no lo sabes, haz lo siguiente:

1. Ir al http://www.lfd.uci.edu/~gohlke/pythonlibs
2. Descargar las versiones más recientes de `numpy+mkl`, `scipy`, y `matplotlib`. Tienes que tener cuidado de escoger la buena   
   versión para tu computadora. Todas estas tienen la forma general ``nombreDelPaquete-versiónDelPaquete-versiónDePython- 
   númeroDeBits.whl``. Asegúrate de descargar el archivo apropiado (si no sabes el número de bits de du programa Python, es casi 
   seguramente 32). Por ejemplo, para SciPy en Python 3.6 con un Python de 32 bits, escogerías ``scipy-0.18.1-cp36-cp36m-win32.whl``.
3. ¡Bravo! Ahora, hay que instalar los paquetes que acabaste de cargar. Va a la línea de comanda (se encuentra en la 
   lista de aplicaciones de tu computadora) y escribe el siguiente:

      :command:`pip install C:\\Users\\jeanne\\Downloads\\numpy‑1.11.3+mkl‑cp36‑cp36m‑win32.whl`

   Después, pulse “Intro”. Por supuesto, tienes que cambiar la última parte para corresponder a dónde tú guardaste el
   paquete NumPy en tu computador cuando lo descargaste. Ver la imagen para un ejemplo:
  
.. image:: Imágenes/Ejemplo_instalación_paquetes.png
   :scale: 90 %
   :align: center
   :alt: Ejemplo de la instalación de paquetes de Python precompilados con la línea de comanda de Windows.

4. Repetir etapa 3 con con SciPy y después con Matplotlib.
5. ¡Casi terminado! Ahora, solamente tienes que ir a https://www.microsoft.com/es-ES/download/details.aspx?id=53840 y 
   descargar el ``C++ 2015 redistributable`` (toma la versión terminando el ``…x86.exe`` si tienes Python de 32 bits (si no lo
   sabes, toma éste) y en ``…x64.exe`` si tienes Python de 64 bits. Después, instálalo. Por razones obscuras, SciPy no
   funciona en Windows sin éste.
6. Y por fin, por supuesto, instalar Tinamit sí mismo en la línea de comanda así:

      :command:`pip install tinamit`
     
 Bueno, si todo esto te parece un poco incómodo, estoy de acuerdo. Hay una nueva lengua de programación llamada 
 `Julia <http://julialang.org/>`_ que es tan rápida como C y tan intuitiva como Python, y por lo tanto no tiene nada de
 extensiones ajenas en Fortran o en C. Pero me di cuenta demasiado tarde y ahora no voy a reescribir todo el programa de
 Tinamit en Julia (después de todo, tengo una tesis que escribir). Lo siento.

Uso con PyCharm
^^^^^^^^^^^^^^^
Para personas que piensan hacer más con Tinamit que usar el IGU, recomiendo muy fuertemente que usen la versión 
Comunitaria (gratis) de PyCharm (https://www.jetbrains.com/pycharm). PyCharm es para Python lo que Word es para documentos
de texto, y te salvará de muchos dolores de cabeza (por una cosa, te dice dónde has hecho un error).

Es bastante fácil usar PyCharm; después de instalarlo, simplemente hay que abrir la copia local de Tinamit en el editor y
empezar a escribir tu código. Si quieres contribuir a Tinamit, puedes usar PyCharm para conectar tu versión con la página
de Tinamit en GitHub (así siempre tendrás la versión más recién). Contáctame (julien.malard@mail.mcgill.ca) si estás 
interesada.




