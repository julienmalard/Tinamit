Uso de datos
============
Puedes utilizar datos externos en Tinamït para especificar valores de variables en simulaciones, para alimentar
calibraciones, y para efectuar validaciones.

Importación
-----------
En Tinamït, una base de datos (:class:`~tinamit.datos.bd.BD`) está compuesto de una a más fuentes
(:class:`~tinamit.datos.fuente.Fuente`). Fuentes pueden representar datos en formato ``.csv``
(:class:`~tinamit.datos.fuente.FuenteCSV`), diccionarios (:class:`~tinamit.datos.fuente.FuenteDic`),
``Dataset`` o ``DataArray`` de ``xarray`` (:class:`~tinamit.datos.fuente.FuenteBaseXarray` y
:class:`~tinamit.datos.fuente.FuenteVarXarray`, respectivamente), o un ``DataFrame`` de ``pandas``
(:class:`~tinamit.datos.fuente.FuentePandas`).

Simulaciones
------------
Las bases de datos se pueden utilizar para

Si solamente quieres especificar valores de parámetros, puedes pasar un

:func:`~tinamit.mod.extern.gen_extern`

Calibraciones
-------------


Validaciones
------------

Regiones
--------



.. plot::
   :include-source: True
   :context: reset

   import matplotlib.pyplot as plt
   import numpy as np


   from tinamit.conect import Conectado
   from tinamit.ejemplos import obt_ejemplo


