Envolturas BF
=============
Cada modelo BF requiere la presencia de una envoltura especial que maneja su interacción (simulación, intercambio
de variables) con Tinamït.

.. note::
   Todas las envolturas son subclases de :class:`~tinamit.envolt.bf.ModeloBF`. No obstante, Tinamït viene con clases
   especiales para simplificar tu vida con casos de modelos más compicados.


¿Cómo escoger la clase pariente? Si tu modelo da resultados con el mismo paso de tiempo con el cual puede avanzar
(por ejemplo, da resultados mensuales y avanza con paso mensual), entonces es un :ref:`modelo sencillo <mod_sencillo>`.
Si da resultados con paso más pequeño que el paso con el cual puede avanzar (por ejemplo, un modelo hidrológico que
simula 1 año a la vez pero después devuelve resultados diarios), entonces es un :ref:`modelo determinado <mod_deter>`.

Si tu modelo tiene subdivisiones temporales adicionales (p. ej., SAHYSMOD simula por un año, pero después
devuelve datos por `estaciones` de duración de entre 1 a 12 meses), entonces es un :ref:`modelo bloques <mod_bloq>`.

Y, por fin, si no sabes antes de simular cuánto tiempo va a simular (p. ej., modelos de cultivos que corren hacia
la cosecha), entonces tienes un :ref:`modelo indeterminado <mod_indeter>`.

.. _mod_sencillo:

Modelos Sencillos
-----------------
Siendo modelos sencillos, las envolturas basadas directamente en :class:`~tinamit.envolt.bf.ModeloBF` solamente
deben implementar las funciones siguientes:

#. :func:`~tinamit.Modelo.unidad_tiempo`: Devuelve la unidad de tiempo del modelo.
#. :func:`~tinamit.Modelo.incrementar`: Avanza el modelo.
#. :func:`~tinamit.Modelo.__init__`: Inicializa el modelo. En la llamada a `super().__init__` debes incluir un objeto :class:`~tinamit.mod.VariablesMod` con los variables del modelo.

Funciones y atributos opcionales:

#. :func:`~tinamit.Modelo.paralelizable`: Indica si el modelo se puede paralelizar para ahorar tiempo.
#. :func:`~tinamit.Modelo.iniciar_modelo`: Acciones llamadas justo antes de la simulación.
#. :func:`~tinamit.Modelo.cerrar`: Efectua acciones de limpieza al final de una simulación.
#. :func:`~tinamit.Modelo._correr_hasta_final`: Permite el modelo de combinar pasos de simulación cuando posible para ser más rápido.
#. :func:`~tinamit.Modelo.instalado`: Verifica si el modelo correspondiendo a la envoltura está instalado en la computadora o no.
#. `Modelo.idioma_orig`: Indica el idioma de los nombres de variables del modelo.

.. warning::
   Tu implementación de :func:`~tinamit.Modelo.incrementar` **debe** incluir una llamada a
   `super().incrementar(rebanada)` al final para que valores de parámetros externos y de clima se actualicen
   correctamente.
   Igualmente, cualquier reimplementación de :func:`~tinamit.Modelo.iniciar_modelo` **debe** incluir una llamada a
   `super().iniciar_modelo(corrida)` al final.

En la función :func:`~tinamit.Modelo.incrementar`, se puede acceder los variables del modelo con
`símismo.variables["nombre del variable"]`, obtener su valor con :func:`~tinamit.mod.Variable.obt_val`, y cambiar
su valor con :func:`~tinamit.mod.Variable.poner_val`:

.. code-block:: python

   lago = símismo.variables['Lago']
   val_lago = lago.obt_val()

   nuevo_valor = 100
   lago.poner_val(nuevo_valor)


.. _mod_deter:

Modelos Determinados
--------------------
Modelos determinados (:class:`~tinamit.envolt.bf.ModeloDeterminado`) simulan por un periodo fijo, y después devuelven
egresos de manera retroactiva. Muchos modelos biofísicos (SWAT, DSSAT, STICS) funcionan (o pueden funcionar) así.

El paso del modelo sigue siendo la unidad de tiempo de los egresos (p. ej., días), y se agrega el concepto de un
``ciclo``, o el tiempo mínimo que se puede efectuar una simulación (p. ej., 1 año).

Funciones obligatorias:

#. :func:`~tinamit.ModeloDeterminado.unidad_tiempo`: Devuelve la unidad de tiempo de los **egresos** del modelo.
#. :func:`~tinamit.ModeloDeterminado.avanzar_modelo`: Avanza el modelo de un cierto número de **ciclos**.
#. :func:`~tinamit.ModeloDeterminado.__init__`: Inicializa el modelo. En la llamada a `super().__init__` debes incluir un objeto :class:`~tinamit.envolt.bf.VariablesModDeter` con los variables del modelo.

.. note::
   No se implementa :func:`~tinamit.Modelo.incrementar` en modelos determinados. Tinamït lo implementa automáticamente
   y llama :func:`~tinamit.Modelo.avanzar_modelo` en los momentos oportunos de la simulación.

Modelos determinados pueden tener variables que cambian con el paso (:class:`~tinamit.envolt.bf.VarPasoDeter`)
y otros que cambian con el ciclo (:class:`~tinamit.mod.Variable`).
Ambos se pueden pasar al :class:`~tinamit.envolt.bf.VariablesModDeter` de la inicialización.

Para cambiar los valores de :class:`~tinamit.envolt.bf.VarPasoDeter` en la función
:func:`~tinamit.Modelo.avanzar_modelo`, se llama :class:`~tinamit.envolt.bf.VarPaso.poner_vals_paso` con
una matriz de valores para todos los pasos en el ciclo presente.
Para obtener su valor en el paso actual, se llama :class:`~tinamit.envolt.bf.VarPaso.obt_val`, o sino
:class:`~tinamit.envolt.bf.VarPaso.obt_vals_paso` para obtener la matriz de sus valores para todos los
pasos en el ciclo actual.

.. note::
   Tinamït se encarga de actualizar los valores de los variables por paso según el paso actual del modelo.

Igualmente pueden implementar todas las funciones opcionales de :class:`~tinamit.envolt.bf.ModeloBF`.

.. _mod_bloq:

Modelos Bloques
---------------
Modelos bloques (:class:`~tinamit.envolt.bf.ModeloBloques`) son una subclase de
(:class:`~tinamit.envolt.bf.ModeloDeterminado`). Además de pasos y ciclos, tienen el concepto de `bloques`.
En su simulación, un ciclo contiene varios bloques hechos de cantidades variables de pasos.

Funciones obligatorias:

#. :func:`~tinamit.ModeloBloques.unidad_tiempo`: Devuelve la unidad de tiempo de **base** de los **egresos** del modelo. Por ejemplo, si el modelo simula por año y devuelve datos por tres estaciones de 4, 5 y 3 meses, entonces la unidad de tiempo sería `mes`.
#. :func:`~tinamit.ModeloBloques.avanzar_modelo`: Avanza el modelo de un cierto número de **ciclos**.
#. :func:`~tinamit.ModeloBloques.__init__`: Inicializa el modelo. En la llamada a `super().__init__` debes incluir un objeto :class:`~tinamit.envolt.bf.VariablesModBloques` con los variables del modelo.

Modelos bloques pueden tener variables bloques (:class:`~tinamit.envolt.bf.VariablesModBloques`), igual que variables
que cambian con el paso (:class:`~tinamit.envolt.bf.VarPasoDeter`) y otros que cambian con el ciclo
(:class:`~tinamit.mod.Variable`).

.. note::
   Tinamït actualiza automáticamente el paso, el bloque y el ciclo de sus variables (con los valores, por supuesto).

Igualmente pueden implementar todas las funciones opcionales de :class:`~tinamit.envolt.bf.ModeloBF`.

.. _mod_indeter:

Modelos Indeterminados
----------------------
Modelos indeterminados (:class:`~tinamit.envolt.bf.ModeloIndeterminado`) avanzan por periodos de tiempo indeterminados
cada vez que se simulan. Tienen el concepto de ciclos, pero el tamaño del ciclo varia entre simulaciones.

Funciones obligatorias:

#. :func:`~tinamit.ModeloIndeterminado.unidad_tiempo`: Devuelve la unidad de tiempo de los **egresos** del modelo.
#. :func:`~tinamit.ModeloIndeterminado.mandar_modelo`: Avanza el modelo.
#. :func:`~tinamit.ModeloIndeterminado.__init__`: Inicializa el modelo. En la llamada a `super().__init__` debes incluir un objeto :class:`~tinamit.envolt.bf.VariablesModIndeterminado` con los variables del modelo.

En :class:`~tinamit.envolt.bf.VariablesModIndeterminado`, se pueden incluir variables cuyos valores
cambian con el paso (:class:`~tinamit.envolt.bf.VarPasoIndeter`), tanto como variables cuyos valores quedan
constantes adentro del mismo ciclo (:class:`~tinamit.mod.Variable`).

En :func:`~tinamit.ModeloIndeterminado.mandar_modelo`, se puede utilizar las mismas funciones que con modelos
determinados para establecer y acceder los valores de los variables.

Igualmente pueden implementar todas las funciones opcionales de :class:`~tinamit.envolt.bf.ModeloBF`.

Variables clima
---------------
Si tu modelo incluye variables climáticos, puedes especificarlos con la función
:func:`~tinamit.Modelo.conectar_var_clima` en el `__init__()` de la clase. Tinamït se encargará de la
actualización del valor del variables cuando se efectua una simulación con clima activado.

.. note::
   Si tu modelo requiere datos de manera más sofisticada (por ejemplo, DSSAT debe guardar en un archivo externo
   todos los datos climáticos *antes* de empezar la simulación), puedes acceder el objeto de
   :class:`~tinamit.mod.clima.Clima` de la corrida actual (si hay) con `símismo.corrida.clima` y llamar sus
   funciones :func:`~tinamit.mod.clima.Clima.obt_datos` o :func:`~tinamit.mod.clima.Clima.obt_todos_vals`.

Configuración
-------------
Puedes incluir variables de configuración en tu envoltura (p. ej., la ubicación de un archivo ejecutable).
Se obtiene el valor con :func:`~tinamit.Modelo.obt_conf`, y usuarias pueden establecer su valor con
`MiEnvoltura.estab_conf("llave", "valor")`. Por ejemplo:

.. code-block:: python

   from tinamit.envolt.sahysmod.bf import ModeloSAHYSMOD
   ModeloSAHYSMOD.estab_conf("exe", "C:\\Camino\\hacia\\mi\\SAHYSMODConsole.exe")

Pruebas
-------
Siempre es buena idea tener pruebas para saber si tu envoltura funciona bien o no. Tinamït te permite integrar
pruebas de lectura de datos, de lectura de egresos y de simulación con tus envolturas.

Puedes implementar las funciones :func:`~tinamit.envolt.bf.ModeloBF.prb_ingreso`,
:func:`~tinamit.envolt.bf.ModeloBF.prb_egreso`,  o :func:`~tinamit.envolt.bf.ModeloBF.prb_simul` para tu modelo.

Después, puedes integrar las funciones :func:`~tinamit.mod.prbs.verificar_leer_ingr`,
:func:`~tinamit.mod.prbs.verificar_leer_egr`, y :func:`~tinamit.mod.prbs.verificar_simul` con tus pruebas
automáticas para comprobar que todo están bien con tu envoltura.
La primera vez que corren las pruebas, Tinamït guardará en el disco los resultados de la lectura de datos y de la
simulación. Asegúrate que estén correctos los variables. Si, en el futuro, tu envoltura ya no da los mismos
resultados, Tinamït te avisará de un error.

.. note::
   Estas funciones se aplican automáticamente a todas las envolturas incluidas con la distribución de Tinamït.


Distribución
------------
Puedes compartir tu nueva envoltura como paquete Python independiente. Igualmente puedes contribuirlo al código fuente
de Tinamït, después de cual todas las usuarias de Tinamït podrán acceder tu envoltura.
