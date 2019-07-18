Referencia de envolturas
========================
Abajo puedes encontrar información sobre todas las envolturas que vienen con Tinamït.
Si quieres agregar una nueva, `contáctenos <https://github.com/julienmalard/Tinamit/issues/new/choose>`_
y la podremos :doc:`desarrollar juntos </des/envolt_bf>`.

Modelos DS
==========
Envolturas incluidas en Tinamït:

* **PySD**: Implementación de modelos DS en puro Python. Más rápido que Vensim, pero no incluye todas las
  funcionalidades (por el momento). Ver su `documentación <https://pysd.readthedocs.io/>`_ aquí. Puede leer modelos
  en formato `.mdl` de Vensim, tanto como el estándar `.xmile` (utilizado, entre otros, por Stella).
* **Vensim**: Un programa de MDS bastante popular. Desafortunadamente, requiere la versión pagada (DSS) para conectar
  con Tinamït. Ver su `página oficial <http://vensim.com/>`_.

Modelos BF
==========
Envolturas incluidas en Tinamït:

* **SAHYSMOD**: Modelo de salinidad de suelos. Ver su `documentación <https://www.waterlog.info/sahysmod.htm>`.
  Para uso con Tinamït deberás descargar una versión especial modificada para funcionar desde la línea
  de comanda `aquí <https://github.com/AzharInam/Sahysmod-SourceCode/releases>`_
  (quieres el ``SahysModConsole.exe``).

Envolturas planeadas:

* **PCSE**: Modelo de cultivos en puro Python.
* **DSSAT**: Modelo de cultivos bien popular.
* **SWAT+**: Modelo hidrológico.