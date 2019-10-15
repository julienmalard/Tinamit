Clima
=====
Tinamït puede incorporar datos de clima de manera automática, incluso con escenarios de cambios climáticos.

.. note::
    Tinamït emplea ``تقدیر`` (``taqdir``) para obtener datos de cambios climáticos. Si vas a hacer muchas simulaciones
    con predicciones futuras, se recomienda que leas su `documentación <https://taqdir.readthedocs.io/es/latest>`_.

Especificar variables
---------------------
Si tienes un variable climático en un modelo DS, puedes especificarlo con la función
:func:`~tinamit.mod.Modelo.conectar_var_clima`.

.. code-block:: python

   from tinamit.envolt.mds import gen_mds

   mod = gen_mds('Mi modelo.xmile')
   mod.conectar_var_clima(var='Lluvia', var_clima='بارش', combin='total', conv=0.001)
   mod.conectar_var_clima(var='Temperatura', var_clima='درجہ_حرارت_اوسط', combin='prom', conv=1)


El parámetro ``combin`` especifica cómo se deben combinar los datos climáticos de varios días si el modelo se simula
con un paso de más de un día. Si es ``prom``, se tomará el promedio; si es ``total``, se tomará el total de los días
incluidos.

.. warning::
   El parámetro ``var_clima`` **debe** ser un nombre de variable reconocido por taqdir (ver su
   `documentación <https://taqdir.readthedocs.io/ur/latest/malumat>`_).
   Igualmente, si la unidad del variable en tu modelo no corresponde a la unidad del variable en taqdir, tendrás
   que especificar el factor de conversión en ``conv``.

Para modelos BF, la conexión ya debería haberse efectuada en la envoltura específica al modelo, así que no deberías
tener que hacer nada.

Correr
------
Después crearemos un objeto :class:`~tinamit.mod.clima.Clima` para especificar el clima para nuestro lugar. El
``escenario`` de cambios climáticos sirve para simulaciones del futuro (taqdir obtendrá automáticamente los datos
de cambios climáticos; ver `aquí <https://taqdir.readthedocs.io/es/latest/nmune/mrksm5.html>`_).

.. code-block:: python

   from tinamit.mod.clima import Clima

   mi_clima = Clima(lat=31.569, long=74.355, elev=10, escenario='8.5')
   t = EspecTiempo(365*50, f_inic='2020-01-01')
   mod.simular(t, clima=mi_clima)

Si tienes tus propios datos observados, también los puedes incluir en el parámetro ``fuentes`` que corresponde
directamente al parámetro ``ذرائع`` de taqdir.

.. code-block:: python

   from تقدیر.ذرائع import جےسن as Json

   fuente = Json('DatosDeMiEstaciónClimáticaPrivadaQueNoVoyACompartirConNadie.json', 31.569, 74.355, 100)

   mod.simular(t, clima=Clima(lat=31.569, long=74.355, elev=10, escenario='8.5', fuentes=(fuente,)))


Te recomendamos que leas la documentación de taqdir si quieres poder aprovechar te todas sus funcionalidades
(extensión de datos, interpolación geográfica, desagregación temporal y mucho más).
