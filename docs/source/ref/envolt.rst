Envolturas
==========
Abajo puedes encontrar información sobre todas las envolturas que vienen con Tinamït.
Si quieres agregar una nueva, `contáctenos <https://github.com/julienmalard/Tinamit/issues/new/choose>`_
y la podremos :doc:`desarrollar juntos </des/envolt_bf>`.

Modelos DS
----------
Envolturas incluidas en Tinamït:

* **PySD** (:class:`~tinamit.envolt.mds.pysd.ModeloPySD`): Implementación de modelos DS en puro Python.
  Más rápido que el DLL de Vensim, en general, pero no incluye todas sus funcionalidades (por el momento).
  Ver su `documentación <https://pysd.readthedocs.io/>`_ aquí. Puede leer modelos
  en formato ``.mdl`` de Vensim, tanto como el estándar ``.xmile`` (utilizado, entre otros, por Stella).
* **Vensim** (:class:`~tinamit.envolt.mds.vensim_dll.ModeloVensimDLL`): Un programa de MDS bastante popular.
  Desafortunadamente, requiere la versión pagada (DSS) para conectar con Tinamït.
  Ver su `página oficial <http://vensim.com/>`_. Además, solamente funciona en Windows.
  Con el DLL de Vensim, primero hay que ir a cada variable en tu modelo Vensim que quieres que pueda recibir valores
  desde el modelo biofísico y escoger ``Gaming`` como tipo de variable. Después, hay que publicar el modelo en formato
  ``.vpm``.

Modelos BF
----------
Envolturas incluidas en Tinamït:

* **SAHYSMOD** (:class:`~tinamit.envolt.bf.sahysmod.ModeloSAHYSMOD`): Modelo de salinidad de suelos.
  Ver su `documentación <https://www.waterlog.info/sahysmod.htm>`_.
  Para uso con Tinamït deberás descargar una versión especial modificada para funcionar desde la línea
  de comanda `aquí <https://github.com/julienmalard/Sahysmod-SourceCode/releases>`_.

Envolturas planeadas:

* **PCSE**: Modelo de cultivos en puro Python, ver su `documentación <https://pcse.readthedocs.io/en/stable/>`_.
* **DSSAT**: Modelo de cultivos bien popular. Descarga `aquí <https://dssat.net/>`_.
* **SWAT+**: Modelo hidrológico, gratis y de fuente abierta. Descarga `aquí <https://swat.tamu.edu/software/plus/>`_.
