Geografía
=========
Tinamït cuenta con funcionalidades de datos geográficos para simulaciones, calibraciones y validaciones.

Especificación
--------------
Primero tenemos que especificar nuestra geografía. Ésta está compuesta de lugares (:class:`~tinamit.geog.región.Lugar`)
de distintos niveles (:class:`~tinamit.geog.región.Nivel`). Por ejemplo, en el nivel departamental podremos encontrar
varios muninicipios.

.. code-block:: python

   from tinamit.geog.región import Nivel, Lugar

   muni = Nivel('Municipio')
   dept = Nivel('Departamento', subniveles=muni)
   terr = Nivel('Territorio', subniveles=muni)
   país = Nivel('País', subniveles=[dept, terr])

   muni1, muni2, muni3 = [Lugar('Muni%i' % i, nivel=muni, cód='M' + str(i)) for i in range(1, 4)]

   dept1 = Lugar('Dept1', nivel=dept, cód='D1', sub_lugares=[muni1, muni2])
   dept2 = Lugar('Dept2', nivel=dept, cód='D2', sub_lugares=[muni3])
   terr1 = Lugar('Terr1', nivel=terr, cód='T1', sub_lugares=[muni1])
   terr2 = Lugar('Terr2', nivel=terr, cód='T2', sub_lugares=[muni2])

   guate = Lugar(
       'Guatemala', sub_lugares={muni1, muni2, muni3, dept1, dept2, terr1, terr2},
       nivel=país
   )


O, para ahorar tiempo con geografías más complejas, puedes emplear la función :func:`~tinamit.geog.región.gen_lugares`,
que genera un lugar automáticamente a base de un archivo de ``.csv``.

.. code-block:: python

   from tinamit.geog.región import gen_lugares
   from tinamit.ejemplos import obt_ejemplo

   guate = gen_lugares(obt_ejemplo('geog_guate/geog_guate.csv'), nivel_base='País', nombre='Iximulew')

.. note::
   Puedes especificar niveles paralelos. Por ejemplo, aquí ``Departamento`` y ``Territorio`` son dos maneras
   alternativas de agrupar los municipios de Guatemala.

Calibración
-----------
Se pueden calibrar modelos según datos geográficos. El resultado será una calibración distinta para cada lugar para
el cual tienes datos.

Ecuaciones
^^^^^^^^^^
Tinamït tiene funcionalidades **experimentales** para calibrar ecuaciones con inferencia bayesiana jerárquica.
Esta funcionalidad permite al modelo inferir valores el regiones para las cuales tienes muy poco (o hacia no) datos.
Funciona por calibrar los variables al nivel más alto (por ejemplo, nacional) y después ajustar sus estimos para
cada sublugar según la disponibilidad de datos.

Cada :class:`~tinamit.geog.región.Nivel` en tu geografía corresponderá a un nivel distinto en el modelo jerárquico.

.. warning::
   La calibración con inferencia bayesiana jerárquica es muy emocionante pero también todavía **experimental**.

   Si tus ecuaciones no están bien definidas o si su forma no corresponde con la de los datos, correrá muy
   lentamente la calibración y tus resultados no valdrán nada de todo modo. Siempre es buena idea visualmente
   comparar los resultados con los datos.

Simplemente puedes pasar un objeto :class:`~tinamit.geog.región.Lugar` a :class:`~tinamit.calibs.ec.CalibradorEcOpt`
o al :class:`~tinamit.calibs.ec.CalibradorEcBayes` (ver :doc:`calibs`).

Modelos
^^^^^^^
Calibraciones geográficas se pueden también aplicar al nivel del modelo entero.

.. code-block:: python

   import numpy as np

   from tinamit.calibs.geog_mod import SimuladorGeog, CalibradorGeog
   from tinamit.datos.bd import BD
   from tinamit.datos.fuente import FuenteDic

   paráms = {
            '708': {
                'taza de contacto': 81.25, 'taza de infección': 0.007, 'número inicial infectado': 22.5,
                'taza de recuperación': 0.0375
            },
            '1010': {
                'taza de contacto': 50, 'taza de infección': 0.005, 'número inicial infectado': 40,
                'taza de recuperación': 0.050
            }
   }

   # Unos datos artificiales
   simul = SimuladorGeog(mds).simular(
       t=100, vals_geog=paráms,
       vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
   )
   datos = {
       lg: {ll: v[:, 0] for ll, v in simul[lg].a_dic().items()} for lg in paráms
   }

   datos = BD([
       FuenteDic(datos[lg], 'Datos geográficos', lugares=lg, fechas=np.arange(101)) for lg in paráms
   ])

   calib = CalibradorGeog(mds).calibrar(t=100, datos=datos, líms_paráms=líms_paráms, n_iter=50)


Validación
----------
Se puede validar una calibración geográfica con la clase :class:`~tinamit.calibs.geog_mod.ValidadorGeog`.

.. code-block:: python

   from tinamit.calibs.geog_mod import ValidadorGeog

   valid = ValidadorGeog(mds).validar(
            t=100, datos=datos,
            paráms={lg: {prm: trz['mejor'] for prm, trz in calib[lg].items()} for lg in paráms}
   )