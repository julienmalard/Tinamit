Calibraciones
=============

Calibrar modelos
----------------
Tinamït puede calibrar modelos según variables observados. Las calibraciones se efectuan con calibradores
(:class:`~tinamit.calibs.mod.CalibradorMod`), por ejemplo, :class:`~tinamit.calibs.mod.CalibradorModSpotPy`.

.. code-block:: python

   import numpy as np

   from tinamit.ejemplos import obt_ejemplo
   from tinamit.envolt.mds import gen_mds

   mod = gen_mds(obt_ejemplo('enfermedad/mod_enferm.mdl'))

Generaremos unos datos artificiales (sí, hacemos trampa).

.. code-block:: python

   from tinamit.datos.fuente import FuenteDic

   paráms = {
       'taza de contacto': 81.25,
       'taza de infección': 0.007,
       'número inicial infectado': 22.5,
       'taza de recuperación': 0.0375
   }

   simul = mod.simular(
       t=100, extern=paráms,
       vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
   )
   datos = FuenteDic({ll: v[:, 0] for ll, v in simul.a_dic().items()}, nombre='Datos', fechas=np.arange(101))

Y efectuamos la calibración.

.. code-block:: python

   from tinamit.calibs.mod import CalibradorModSpotPy

   líms_paráms={
       'taza de contacto': (0, 100),
       'taza de infección': (0, 0.02),
       'número inicial infectado': (0, 50),
       'taza de recuperación': (0, 0.1)
   }

   calibs = CalibradorModSpotPy(mod).calibrar(líms_paráms=líms_paráms, datos=datos, n_iter=50)


Calibrar ecuaciones
-------------------
En el caso de modelos de dinámicas de sistemas, también se pueden calibrar los parámetros de ecuaciones individuales
si tienes los datos necesarios.

Las calibraciones se pueden hacer con optimización (:class:`~tinamit.calibs.ec.CalibradorEcOpt`) o con
inferencia bayesiana (:class:`~tinamit.calibs.ec.CalibradorEcBayes`).

.. note::
   Casos sencillos con muchos datos disponibles generalmente se pueden resolver mucho más rápido con optimización
   normal que con la más sofisticada inferencia bayesiana.

El el modelo epidemiológico, el número de contactos con susceptibles se determina por el número de suceptibles y la
taza de contacto según la ecuación ``contactos con suceptibles = Individuos Suceptibles * taza de contacto``.
Suponiendo que tenemos datos para el número de suceptibles y el número de contactos, podemos estimar la taza de
contacto.

.. code-block:: python

   from tinamit.calibs.ec import CalibradorEcOpt
   from tinamit.datos.bd import BD
   from tinamit.datos.fuente import FuenteDic

   n_obs = 100
   taza_contacto = 125
   individuos_suceptibles = np.random.random(n_obs)

   contactos_con_suceptibles = individuos_suceptibles * taza_contacto + np.random.normal(0, 1, n_obs)
   bd = BD(
       fuentes=FuenteDic({
               'contactos con suceptibles': contactos_con_suceptibles,
               'Individuos Suceptibles': individuos_suceptibles,
               'f': np.arange(n_obs)
           },
           nombre='Datos generados',
           fechas='f'
       )
   )

   calibrador = CalibradorEcOpt(
       ec=mod.variables['contactos con suceptibles'].ec, nombre='contactos con suceptibles',
       paráms=['taza de contacto']
   )
   calib_ec = calibrador.calibrar(líms_paráms={'taza de contacto': (0, 200)}, bd=bd)



Validar
-------
Por supuesto, no hay calibración sin validación. (Al menos que tengas que publicar ya.) Las validaciones se
efectuan con :class:`~tinamit.calibs.valid.ValidadorMod`.

.. code-block:: python

   from tinamit.calibs.valid import ValidadorMod

   valid = ValidadorMod(mod).validar(
       t=100, datos=datos, paráms={prm: trz['mejor'] for prm, trz in calibs.items()}
   )
