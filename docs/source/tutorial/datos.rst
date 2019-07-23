Uso de datos
============


.. plot::
   :include-source: True
   :context: reset

   import matplotlib.pyplot as plt
   import numpy as np


   from tinamit.conect import Conectado
   from tinamit.ejemplos import obt_ejemplo

   mds = obt_ejemplo('básico/mds_bosques.mdl')
   bf = obt_ejemplo('básico/bf_bosques.py')

   modelo = Conectado(bf=bf, mds=mds)

   plt.plot(np.arange(10))
