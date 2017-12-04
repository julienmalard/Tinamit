Cómo se emplea Tinamit
======================

Hay dos maneras de usar Tinamit. Si quieres hacerlo sin código cualquier, el IGU (Interfaz de Usuario Gráfico) es para ti.
Si prefieres hacerlo con unas pocas líneas de código (lo cual puede acelerar bastante tu trabajo si tienes muchas simulaciones
diferentes que quieres automatizar), entonces el IPA (Interfaz de Programación de Aplicaciones) es la mejor opción.

Al final, el IGU y el IPA hacen el mismo trabajo (el IGU tiene botones muy lindos para llamar las funciones del IPA de manera
automática). No obstante, nuevas funcionalidades divertidas siempre aparecen en el IPA primero (lo siento).

Para una introducción rápida, ver:

.. contents::
   :depth: 1

   IGU (Interfaz) <IGU>
   IPA (Programa) <IPA>
   Avanzado <avanzado>

Funcionalidades actuales y futuras de Tinamït
---------------------------------------------
.. csv-table:: 
   :header: "Funcionalidad", "IGU", "IPA"
   :align: center

   "Conectar modelos BF y DS", "X", "X"
   "Conversión de unidades de variables", "X", "X"
   "Ajustar el paso y tiempo final", "X", "X"
   "Simular modelos conectados", "", "X"
   "Traducciones", "X", ":("
   "Escenarios de políticas", "", "X"
   "Cambios climáticos", "", "X"
   "Mapas espaciales", "", "X"
   "Conectar 3+ modelos", "", "¿?"
   "Análisis de sensibilidad", "", ""
   "Análisis de incertidumbre", "", ""
   "Calibración y validación", "", ""
   "Simulaciones en paralelo", "", ""
   
¿? = En teoría, pero no hemos intendado. Por favor avísanos si te funciona.

Preparación pre-uso
-------------------
No importe cuál del IPA o el IGU eliges usar, hay unas acciones preparatorias de las cuales no podrás escaparte.

Preparación del modelo DS
^^^^^^^^^^^^^^^^^^^^^^^^^
Tendrás que preparar el modelo de dinámicas de los sistemas antes de poder conectarlo. Para Vensim (por el momento, Tinamït
funciona con Vensim solamente), primero hay que ir a cada variable en tu modelo Vensim que quieres que pueda recibir valores 
desde el modelo biofísico y escoger “Gaming” como tipo de variable. Después, hay que publicar el modelo en formato .vpm.

Preparación del modelo biofísico
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Si ya existe una envoltura específica para el modelo biofísico, no tienes que hacer nada más. Si no está disponible ya, tendrás
que escribir una (o convencer a alguien de hacerlo para ti). 
