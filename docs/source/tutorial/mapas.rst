Mapas
=====
Tinamït viene con algunas funcionalidades para dibujar mapas de resultados de simulación. Todos los mapas están
compuestos de objetos :class:`~tinamit.geog.mapa.Forma`. Cada :class:`~tinamit.geog.mapa.Forma` está vinculada
con un archivo ``.shp``.

Formas dinámicas
----------------
Formas dinámicas (:class:`~tinamit.geog.mapa.FormaDinámica`) son las formas cuyos colores varían según los resultados
de una simulación. Incluyen :class:`~tinamit.geog.mapa.FormaDinámicaNumérica`, la cual toma sus valores en formato
de ``np.ndarray`` o de lista, y :class:`~tinamit.geog.mapa.FormaDinámicaNombrada`, la cual quiere sus datos en
formato de diccionario.

Los mapas se pueden dibujar desde una matriz de un variable multidimensional en un modelo, o sino de una simulación
de grupo donde cada simulación individual representa otra región en el mapa. Ambas situaciones se manejan por
:func:`~tinamit.geog.mapa.dibujar_mapa_de_res`.

Simulaciones por grupo
^^^^^^^^^^^^^^^^^^^^^^
En este ejemplo, correremos un modelo de epidemiología
con distintas tazas de contacto para cada departamento de Guatemala.

.. plot::
   :include-source: True
   :context: reset

   import numpy as np

   from tinamit.ejemplos import obt_ejemplo
   from tinamit.envolt.mds import gen_mds
   from tinamit.geog.región import gen_lugares
   from tinamit.geog.mapa import FormaDinámicaNombrada, dibujar_mapa_de_res
   from tinamit.mod import OpsSimulGrupo

   mds = gen_mds(obt_ejemplo('enfermedad/mod_enferm.mdl'))
   guate = gen_lugares(obt_ejemplo('geog_guate/geog_guate.csv'), nivel_base='País', nombre='Iximulew')
   forma_deptos = obt_ejemplo('geog_guate/deptos.shp')

   ops = OpsSimulGrupo(
       t=50,
       extern=[{'taza de contacto': np.random.random() * 500} for i in range(1, 23)],
       nombre=[str(i) for i in range(1, 23)]
   )
   res = mds.simular_grupo(ops, nombre='Epidemiología')

   frm = FormaDinámicaNombrada(forma_deptos, col_id='COD_DEP', escala_colores=-1)
   dibujar_mapa_de_res(forma_dinámica=frm, res=res, var='Individuos Infectados', t=16)

.. note::
   El nombre de cada simulación en el grupo debe corresponder con el nombre de una forma en el archivo ``.shp`` tal
   como especificado en la columna ``col_id``.

   Alternativamente, puedes utilizar una :class:`~tinamit.geog.mapa.FormaDinámicaNumérica`; en ese caso se asiñarán
   los resultados a las formas según su orden en ``OpsSimulGrupo``, nada más.

Variables multidimensionales
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Aplicaremos un modelo sencillo de bosques y lluvia a un mapa de la región del Rechna Doab (رچنا دوآب) en Pakistán.
Este mapa divide la región en 215 polígonos, cada cual corresponde a un punto en el variable ``Bosque``
multidimensional.

.. plot::
   :include-source: True
   :context: close-figs

   from tinamit.ejemplos.sencillo.bf_bosques import PruebaBF
   from tinamit.geog.mapa import FormaDinámicaNumérica

   mod = PruebaBF(215)
   polígonos = obt_ejemplo('rechna_doab/polígonos.shp')

   extern = {'Bosques': np.random.random(215)*1e6}
   res = mod.simular(t=10, extern=extern, nombre='Cobertura forestal')

   frm = FormaDinámicaNumérica(polígonos, col_id='Id')
   dibujar_mapa_de_res(forma_dinámica=frm, res=res, var='Bosques', t=10)


Formas estáticas
----------------
También puedes agregar formas estáticas (:class:`~tinamit.geog.mapa.FormaEstática`), que no depienden de los resultados
de una simulación y que se agregan solamente por razones estéticas.

Por el momento, tienes:

* Cuerpos de agua: :class:`~tinamit.geog.mapa.Agua`
* Bosques: :class:`~tinamit.geog.mapa.Bosque`
* Calles: :class:`~tinamit.geog.mapa.Calle`
* Zonas urbanas: :class:`~tinamit.geog.mapa.Ciudad`

.. plot::
   :include-source: True
   :context: close-figs

   from tinamit.geog.mapa import Agua

   canales = Agua(obt_ejemplo('rechna_doab/canal.shp'), llenar=False)
   dibujar_mapa_de_res(forma_dinámica=frm, otras_formas=canales, res=res, var='Bosques', t=10)
