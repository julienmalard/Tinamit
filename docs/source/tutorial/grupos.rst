Simulaciones en grupo
=====================
Si tienes muchas simulaciones para efectuar, puedes ahorar tiempo por hacerlas por grupos con la función
:func:`~tinamit.mod.Modelo.simular_grupo` y un objeto de simulaciones por grupos
(:class:`~tinamit.mod.corrida.OpsSimulGrupo`). Igualmente se pueden paralelizar las corridas para ahorar más tiempo.


.. code-block:: python

   from tinamit.mod import OpsSimulGrupo
   from tinamit.envolt.mds import gen_mds

   mod = gen_mds('Mi modelo.xmile')

   vals_extern = [{'Política 1': 0, 'Política 2': 1}, {'Política 1': 1, 'Política 2': 0}]

   ops = OpsSimulGrupo(t=[100, 150], extern=vals_extern)
   res = mod.simular_grupo(ops)

En el ejemplo arriba, simularemos el modelo con ``Política 2`` para 100 pasos, y con ``Política 1`` por 150 pasos.

.. warning::
   Cada opción con valores múltiples debe ser una lista, y cada lista presente en las opciones debe tener el mismo
   tamaño.

Opciones que no se especificaron en formato de lista se aplicarán a todas las corridas. En el ejemplo abajo, cada
política se correrá por 100 pasos.

.. code-block:: python

   res = mod.simular_grupo(OpsSimulGrupo(t=100, extern=vals_extern))

Combinaciones
-------------
También se puede ejecutar todas las combinaciones posibles para las opciones de simulación con un objeto
:class:`~tinamit.mod.corrida.OpsSimulGrupoCombin`. Por ejemplo, puedes simular todas las combinaciones de
distintas políticas con varios escenarios de cambios climáticos.


.. code-block:: python

   from tinamit.mod.clima import Clima

   clima_malo = Clima(lat=31.569, long=74.355, elev=10, escenario='2.6')
   clima_peor = Clima(lat=31.569, long=74.355, elev=10, escenario='4.5')
   clima_fritos = Clima(lat=31.569, long=74.355, elev=10, escenario='8.5')

   t = EspecTiempo(365*50, f_inic='2020-01-01')

   ops = OpsSimulGrupoCombin(t=t, extern=vals_extern, clima=[clima_malo, clima_peor, clima_fritos])
   res = mod.simular_grupo(ops)

   # Para ver cuáles combinaciones corresponden con cada resultado (en orden)
   list(ops)