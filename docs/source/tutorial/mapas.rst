Mapas
=====
Tinamït viene con algunas funcionalidades para dibujar mapas de resultados de simulación. Todos los mapas están
compuestos de objetos :class:`~tinamit.geog.mapa.Forma`. Cada :class:`~tinamit.geog.mapa.Forma` está vinculada
con un archivo ``.shp``.

Formas dinámicas
----------------
Formas dinámicas (:class:`~tinamit.geog.mapa.FormaDinámica`) son las formas cuyos colores varían según los resultados
de una simulación.

Los mapas se pueden dibujar desde una matriz de un variable multidimensional en un modelo, o sino de una simulación
de grupo donde cada simulación individual representa otra región en el mapa.

Variables multidimensionales
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
    frm = FormaDinámicaNumérica(arch_frm_numérica, col_id='Id')
    extern = {'Vacío': np.arange(len(frm.ids))}
    res = ModeloPrueba(dims=(215,)).simular(t=10, extern=extern)
    dibujar_mapa_de_res(forma_dinámica=frm, res=res, var='Vacío', t=3, directorio=símismo.dir_)


Simulaciones por grupo
^^^^^^^^^^^^^^^^^^^^^^


.. plot::
   :include-source: True
   :context: reset

   import numpy as np
   import matplotlib.pyplot as plt

   from tinamit.ejemplos import obt_ejemplo
   from tinamit.envolt.mds import gen_mds
   from tinamit.geog.región import gen_lugares

   mds = gen_mds(obt_ejemplo('enfermedad/mod_enferm.mdl'))
   guate = gen_lugares(obt_ejemplo('geog_guate/geog_guate.csv'), nivel_base='País', nombre='Iximulew')
   forma_deptos = obt_ejemplo('geog_guate/departamentos_gtm_fin.shp')

   ops = OpsSimulGrupo(
       t=50,
       extern=[{'taza de contacto': np.random.random() * 500} for i in range(1, 23)],
       nombre=[str(i) for i in range(1, 23)]
   )
   res = mds.simular_grupo(ops)


   frm = FormaDinámicaNombrada(arch_frm_nombrada, col_id='COD_MUNI')
   dibujar_mapa_de_res(forma_dinámica=frm, res=res, var='Vacío', t=3, directorio=símismo.dir_)


Formas estáticas
----------------
También puedes agregar formas estáticas (:class:`~tinamit.geog.mapa.FormaEstática`) que no depienden de los resultados
de una simulación (p. ej., bosques, calles, cuerpos de agua).



