Clima
=====
Tinamït puede incorporar datos de clima de manera automática, incluso con escenarios de cambios climáticos.

.. note::
    Tinamït emplea ``تقدیر`` (``taqdir``) para obtener datos de cambios climáticos. Si vas a hacer muchas simulaciones
    con predicciones futuras, se recomienda que leas su `documentación <https://taqdir.readthedocs.io/es/latest>`_.

Especificar variables
---------------------
Si tienes un variable climático en un modelo DS, puedes especificarlo con la función
:func:`~tinamit.Modelo.conectar_var_clima`.

.. code-block:: python

   from tinamit.envolt.mds import gen_mds

   mod = gen_mds('Mi modelo.xmile')
   mod.conectar_var_clima(var='Lluvia', var_clima='بارش', combin='total', conv=0.001)
   mod.conectar_var_clima(var='Temperatura', var_clima='درجہ_حرارت_اوسط', combin='prom', conv=1)

.. note::
   El parámetro ``var_clima`` **debe** ser un nombre de variable reconocido por taqdir (ver su
   `documentación <https://taqdir.readthedocs.io/ur/latest/malumat>`_).
   Igualmente, si la unidad del variable en tu modelo no corresponde a la unidad del variable en taqdir, tendrás
   que especificar el factor de conversión en ``conv``.

Para modelos BF, la conexión ya debería haberse efectuada en la envoltura específica al modelo, así que no deberías
tener que hacer nada.

Correr
------


