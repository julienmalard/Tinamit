Envolturas MDS
==============
Envolturas para modelos de dinámicas de sistemas son subclases de :class:`tinamit.envolt.mds.ModeloMDS`.

.. note::
   Las envolturas para modelos DS son **universales**. Es decir, la misma envoltura funcionará para todos los modelos
   creados con el mismo programa (p. ej., Vensim), no importe el contenido del modelo sí mismo.

Cómo crear tu envoltura
-----------------------

Funciones y atributos para implementar:

#. :func:`~tinamit.Modelo.unidad_tiempo`: Devuelve la unidad de tiempo del modelo.
#. :func:`~tinamit.Modelo.incrementar`: Avanza el modelo.
#. :func:`~tinamit.Modelo.__init__`: Inicializa el modelo. En la llamada a `super().__init__` debes incluir un objeto :class:`~tinamit.envolt.mds.VariablesMDS` con los variables del modelo.
#. :func:`~tinamit.Modelo.cambiar_vals`: No estríctamente necesario, pero la casi totalidad de modelos DS necesitarán tomar acción específica para cambiar valores de variables en el modelo externo.
#. `ModeloDS.ext`: Una lista de las extensiones de archivo que se pueden leer por la envoltura.

Funciones y atributos opcionales:

#. :func:`~tinamit.Modelo.paralelizable`: Indica si el modelo se puede paralelizar para ahorar tiempo.
#. :func:`~tinamit.Modelo.iniciar_modelo`: Acciones llamadas justo antes de la simulación.
#. :func:`~tinamit.Modelo.cerrar`: Efectua acciones de limpieza al final de una simulación.
#. :func:`~tinamit.Modelo._correr_hasta_final`: Permite el modelo de combinar pasos de simulación cuando posible para ser más rápido.
#. :func:`~tinamit.Modelo.instalado`: Verifica si el modelo correspondiendo a la envoltura está instalado en la computadora o no.

.. warning::
   Tu implementación de :func:`~tinamit.Modelo.incrementar` **debe** incluir una llamada a
   `super().incrementar(rebanada)` al final para que valores de parámetros externos y de clima se actualicen
   correctamente.
   Igualmente, cualquier reimplementación de :func:`~tinamit.Modelo.iniciar_modelo` **debe** incluir una llamada a
   `super().iniciar_modelo(corrida)` al final, y  :func:`~tinamit.Modelo.cambiar_vals` una a
   `super().cambiar_vals(valores)`.

Cada variable en :class:`~tinamit.envolt.mds.VariablesMDS` debe ser uno de :class:`~tinamit.envolt.mds.VarConstante`,
:class:`~tinamit.envolt.mds.VarInic`, :class:`~tinamit.envolt.mds.VarNivel`, o :class:`~tinamit.envolt.mds.VarAuxiliar.

Autogeneración
--------------
La función :func:`~tinamit.envolt.mds.gen_mds` de Tinamït puede escoger automáticamente la envoltura más apropriada
para un archivo dado de modelo DS según el atributo `ModeloMDS.ext` de cada clase de envoltura.
Puedes llamar la función :func:`~tinamit.envolt.mds.registrar_envolt_mds` para registrar tu nueva clase de modelo DS
en Tinamït, y :func:`~tinamit.envolt.mds.olvidar_envolt_mds` para quitarla.

Si estás modificando el código fuente de Tinamït, puedes agregar tu clase a `tinamit.envolt.mds._auto._subclases`
para que se tome automáticamente en cuenta.

Distribución
------------
Puedes compartir tu nueva envoltura como paquete Python independiente. Igualmente puedes contribuirlo al código fuente
de Tinamït, después de cual todas las usuarias de Tinamït podrán acceder tu envoltura.
