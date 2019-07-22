Conectar modelos
================

Ejemplo muy básico
------------------
Empezaremos con un modelo bastante sencillo. Pero demuestra muy bien cómo funciona Tinamït, y no tienes que instalar
cualquier modelo biofísico externo para que te funcione, así que empecemos con este.

Primero vamos a utilizar este modelo de dinámicas de sistemas:

.. image:: /_estático/imágenes/Ejemplos/Ejemplo_básico_modelo_VENSIM.png
   :align: center
   :alt: Modelo Vensim.

El modelo DS determina, dado la lluvia, la cantidad de pesca posible y su impacto en la necesidad de explotar
recursos del bosque.

Del otro lado, el "modelo" biofísico nos da la precipitación según la cubertura forestal.

.. plot::
   :include-source: True
   :context: reset

   import matplotlib.pyplot as plt

   from tinamit.conect import Conectado
   from tinamit.ejemplos import obt_ejemplo

   mds = obt_ejemplo('básico/mds_bosques.mdl')
   bf = obt_ejemplo('básico/bf_bosques.py')

   modelo = Conectado(bf=bf, mds=mds)

   # Vamos a conectar los variables necesarios
   modelo.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)
   modelo.conectar(var_mds='Bosques', var_bf='Bosques', mds_fuente=True)

   # Y simulamos
   res_conex = modelo.simular(200)

   # Visualizar
   f, (eje1, eje2) = plt.subplots(1, 2)
   eje1.plot(res_conex['mds']['Bosques'].vals)
   eje1.set_title('Bosques')
   eje1.set_xlabel('Meses')

   eje2.plot(res_conex['mds']['Lluvia'].vals)
   eje2.set_title('Lluvia')
   eje2.set_xlabel('Meses')

   eje1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

Tambiém comparemos a una corrida sin conexión para ver el impacto de incluir las relaciones entre ambiente y
humano.

.. plot::
   :include-source: True
   :context: close-figs

   from tinamit.envolt.mds import gen_mds
   from tinamit.envolt.bf import gen_bf

   res_mds = gen_mds(mds).simular(200, nombre='Corrida_MDS')
   res_bf = gen_bf(bf).simular(200, nombre='Corrida_BF')

   # Visualizar
   f, (eje1, eje2) = plt.subplots(1, 2)
   eje1.plot(res_conex['mds']['Bosques'].vals, label='Conectado')
   eje1.plot(res_mds['Bosques'].vals, label='Individual')
   eje1.set_title('Bosques')
   eje1.set_xlabel('Meses')

   eje1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

   eje2.plot(res_conex['mds']['Lluvia'].vals)
   eje2.plot(res_bf['Lluvia'].vals, label='Individual')
   eje2.set_title('Lluvia')
   eje2.set_xlabel('Meses')


Unidades de tiempo
------------------


3+ modelos
----------
