.. _avanzado:

Uso avanzado de Tinamït
=======================
Aquí describimos unas funciones más avanzadas de Tinamït. Muchas de estas, por el momento, se puedes acceder únicamente
por el IPA, y no el IGU.

.. contents::

Mapas espaciales
----------------
Tinamït puede dibujar mapas sencillos de los resultados de modelos espaciales. Esto se hace por el objeto
:class:`~tinamit.Geog.Geog.Geografía` de Tinamït.

Primero, creamos el objeto de geografía::

    from tinamit.Geog.Geog import Geografía
    Rechna_Doab = Geografía(nombre='Rechna Doab')

Después, agregamos las regiones que corresponden con los subscriptos (matriz) de los variables espaciales en nuestro
modelo DS con la función `~tinamit.Geog.Geog.Geografía.agregar_regiones.
Estas son las regiones que se colorarán según los resultados::

    base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shape_files')
    Rechna_Doab.agregar_regiones(os.path.join(base_dir, 'Internal_Polygon.shp'), col_orden='Polygon_ID')

.. note:: ``col_orden`` debe ser un atributo numérico del archivo ``.shp``, donde cada número corresponde con el
   índice de esta región en la matriz (subscriptos) del modelo DS. La cuenta puede empezar en 0 o en 1. Si no
   se especifica ``col_orden``, Tinamït supondrá que las regiones del archivo ``.shp`` están en el mismo orden que los
   índices en tu modelo DS, lo cual puede ser mala idea suponer.

Ahora, agregamos otros objeto geográficos puramente estéticos con la función `~tinamit.Geog.Geog.Geografía.agregar_objeto::

    Rechna_Doab.agregar_objeto(os.path.join(base_dir, 'External_Polygon.shp'), color='#edf4da')
    Rechna_Doab.agregar_objeto(os.path.join(base_dir, 'RIVR.shp'), tipo='agua')
    Rechna_Doab.agregar_objeto(os.path.join(base_dir, 'CNL_Arc.shp'), tipo='agua', llenar=False)
    Rechna_Doab.agregar_objeto(os.path.join(base_dir, 'Forst_polygon.shp'), tipo='bosque')
    Rechna_Doab.agregar_objeto(os.path.join(base_dir, 'buildup_Polygon.shp'), tipo='ciudad')
    Rechna_Doab.agregar_objeto(os.path.join(base_dir, 'road.shp'), tipo='calle')

.. note::
   Puedes especificar el ``color`` y la transparencia (``alpha``) del objeto, tanto como si se debe
   llenar o simplemente dibujar el contorno. Para facilitarte la vida, hay unas opciones predeterminadas
   (``ciudad``, ``calle``, ``agua``, ``bosque``) que puedes especificar con ``tipo``.

Cambios climáticos
------------------
También podemos conectar nuestro modelos con observaciones y predicciones climáticas si nuetro modelo tiene variables
climáticos. Esto se hace con la clase :class:`~tinamit.Geog.Geog.Lugar` de Tinamït.

.. warning::::
   Debes tener un modelo de predicciones climáticos, como MarkSim, si quieres poder generar predicciones.
   También puedes pre-descargar archivos de predicciones del sitio internet de MarkSim.

Primero, debemos crear la instancia de :class:`~tinamit.Geog.Geog.Lugar`, con sus coordenadas::

    from tinamit.Geog.Geog import Lugar
    mi_lugar = Lugar(lat=32.178207, long=73.217391, elev=217)

Visto que tenemos observaciones mensuales para unos años, los conectamos con la función
:func:`~tinamit.Geog.Geog.Lugar.observar_mensuales`. ::

    mi_lugar.observar_mensuales(archivo='مشاہدہ بارش.csv', meses='مہینہ', años='سال',
                                cols_datos={'Precipitación': 'بارش (میٹر)'})

``archivo`` es el archivo con los datos, ``meses`` y ``años`` los nombres de las columnas con el mes y el año
(¿¡verdad!?) y ``col_datos`` es un diccionario con la correspondencia de nombres de variables climáticos oficiales
de Tinamït y el nombre actual de la columna en tu base de datos.

.. note::
   Tambien se pueden :func:`~tinamit.Geog.Geog.Lugar.observar_diarios` y :func:`~tinamit.Geog.Geog.Lugar.observar_mensuales`.
   Si tienes datos mensuales o anuales y un modelo necesita datos diarios, Tinamït dividirá la precipitación igualmente
   entre los días del mes o del año.

La opciones actuales (y sus unidades) para variables climáticos son:

* ``Precipitación`` : mm
* ``Radiación solar`` : MJ / m2 / día
* ``Temperatura máxima`` : grados C
* ``Temperatura promedia`` : grados C
* ``Temperatura mínima`` : grados C

.. note::
   Tinamït puede leer archivos con datos numéricos guardaros en escrituras de la mayoría del mundo (por ejemplo,
   १२३, ௧௨௩, ೧೨೩, 一二三, ١٢٣, etc.) Chévere, ¿no? (Yo sé, yo sé.)

