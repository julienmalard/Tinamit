Uso de datos
============
Puedes utilizar datos externos en Tinamït para especificar valores de variables en simulaciones, para alimentar
calibraciones, y para efectuar validaciones.

Datos exógenos
--------------
Puedes especificar valores de parámetros o de variables externos en el transcurso de una simulación.
ٓAquí vamos a hacer una simulación con un modelo sencillo de contagión de una enfermedad.

.. plot::
   :include-source: True
   :context: reset

   import matplotlib.pyplot as plt

   from tinamit.ejemplos import obt_ejemplo
   from tinamit.envolt.mds import gen_mds

   mds = gen_mds(obt_ejemplo('enfermedad/mod_enferm.mdl'))

   extern = {'número inicial infectado': 15}
   res = mds.simular(t=100, extern=extern)

   # Visualizar
   plt.plot(res['Individuos Infectados'].vals)
   plt.title('Población infectada')
   plt.xlabel('Días')
   plt.ylabel('Personas')

Igualmente podemos pasar datos que varían temporalmente. Por ejemplo, la taza de infección puede variar a través
de la epidemía.

.. plot::
   :include-source: True
   :context: close-figs

   from tinamit.tiempo import EspecTiempo
   import numpy as np
   import pandas as pd

   extern = pd.DataFrame(
       data={'taza de infección': np.arange(0.001, 0.005, (0.005-0.001)/100)},
       index=pd.date_range('2000-01-01', periods=100)
   )
   res_base = mds.simular(t=EspecTiempo(100, f_inic='2000-01-01'))
   res_extern = mds.simular(t=EspecTiempo(100, f_inic='2000-01-01'), extern=extern)

   # Visualizar
   plt.plot(res_base['Individuos Infectados'].vals, label='Constante')
   plt.plot(res_extern['Individuos Infectados'].vals, label='Variable')

   plt.legend()
   plt.title('Población infectada')
   plt.xlabel('Días')
   plt.ylabel('Personas')

Si quieres más control sobre el uso de variables externos, puedes utilizar la función
:func:`~tinamit.mod.extern.gen_extern` para generar un objeto :class:`~tinamit.mod.extern.Extern` que puedes pasar
al parámetro ``extern``.

.. note::
   Se puede utilizar datos en formato de ``dict``, ``pd.DataFrame`` o ``xr.Dataset``.

Bases de datos
--------------
Para calibraciones y validaciones, puedes utilizar bases de datos, las cuales te permiten combinar varias fuentes
de datos además de especificar datos geográficos.

En Tinamït, una base de datos (:class:`~tinamit.datos.bd.BD`) está compuesto de una a más fuentes
(:class:`~tinamit.datos.fuente.Fuente`). Fuentes pueden representar datos en formato ``.csv``
(:class:`~tinamit.datos.fuente.FuenteCSV`), diccionarios (:class:`~tinamit.datos.fuente.FuenteDic`),
``Dataset`` o ``DataArray`` de ``xarray`` (:class:`~tinamit.datos.fuente.FuenteBaseXarray` y
:class:`~tinamit.datos.fuente.FuenteVarXarray`, respectivamente), o un ``DataFrame`` de ``pandas``
(:class:`~tinamit.datos.fuente.FuentePandas`).

Ver :doc:`calibs` y :doc:`geog` para más detalles.
