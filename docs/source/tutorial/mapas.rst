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
    frm = FormaDinámicaNumérica(arch_frm_numérica, col_id='Id')
    extern = {'Vacío': np.arange(len(frm.ids))}
    res = ModeloPrueba(dims=(215,)).simular(t=10, extern=extern)
    dibujar_mapa_de_res(forma_dinámica=frm, res=res, var='Vacío', t=3, directorio=símismo.dir_)


Simulaciones por grupo
^^^^^^^^^^^^^^^^^^^^^
    ops = OpsSimulGrupo(t=3, extern=[{'Vacío': 1}, {'Vacío': 3}], nombre=['701', '101'])
    res = ModeloPrueba().simular_grupo(ops)

    frm = FormaDinámicaNombrada(arch_frm_nombrada, col_id='COD_MUNI')
    dibujar_mapa_de_res(forma_dinámica=frm, res=res, var='Vacío', t=3, directorio=símismo.dir_)


Formas estáticas
----------------
También puedes agregar formas estáticas (:class:`~tinamit.geog.mapa.FormaEstática`) que no depienden de los resultados
de una simulación (p. ej., bosques, calles, cuerpos de agua).



