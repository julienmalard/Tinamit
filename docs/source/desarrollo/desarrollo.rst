.. _desarrollo:

Desarrollo de Tinamït
=====================
Tinamït tiene una estructura modular, así que es muy fácil agregar más funcionalidades. En particular, por el desarrollo
de envolturas específicas, se puede agregar compatibilidad con varios programas de modelos
**de dinámicas de sistemas (DS)** y modelos **biofísicos (BF)**. También se pueden contribuir **traducciones** del
interfaz y de la documentación.

Además, Tinamït permite incorporar los resultados de modelos de **predicción climática** en las corridas de modelos
apropiados.

Modelos DS
----------
Tinamït queda compatible con modelos escritos con los programas siguientes. Siempre puedes
:ref:`escribir más <des_mds>`.

* **Vensim**: Un programa de MDS bastante popular. Desafortunadamente, requiere la versión pagada (DSS) para conectar con Tinamït. Ver su `página oficial <http://vensim.com/>`_ y la envoltura.
* **Stella**: Otro programa bastante popular. Ver su `página oficial <https://www.iseesystems.com/store/products/stella-architect.aspx>`_ aquí. Envoltura todavía en trabajo.

Modelos BF
----------
Cada envoltura agrega compatibilidad con un tipo de modelo biofísico distinto. Notar que Tinamït no viene con estos
models incluidos pero simplemente *conecta* con ellos; los tienes que instalar separadamente. Siempre puedes
:ref:`agregar una nueva envoltura <des_bf>` para tu modelo BF preferido. Por el momento, tenemos:

* **SAHYSMOD**: Un modelo de salinidad de suelos. Ver la `documentación completa <https://www.waterlog.info/sahysmod.htm>`_ y la envoltura.
* **DSSAT**: Un modelo de cultivos, que toma en cuenta semilla, clima, suelo y manejo humano. Ver la `documentación completa <https://dssat.net/>`_. (Envoltura en trabajo.)

Modelos de Clima
----------------
Tinamït, por el paquete :py:ref:`taqdir`, ofrece la posibilidad de correr análisis de impactos de cambios climáticos.
Igual que para envolturas de modelos BF, simplemente conecta con estos modelos, no los incluye. Así que los tendrás
que instalar ti misma.

* **Marksim CMIP 5**: Marksim v2 permite generar predicciones climáticas con varios escenarios de cambios climáticos para cualquier región del mundo. Para más información, ver su `documentación oficial <http://www.ccafs-climate.org/pattern_scaling/>`_.
* **Marksim CMIP 3**: ¿Por qué usar CMIP 3 cuando tienes CMIP 5? Bueno, justo en caso, estamos trabajando en agregar compatibilidad con `Marksim <http://www.ccafs-climate.org/pattern_scaling/>`_ v1.

Traducciones
------------
¡Siempre querremos traducciones para hacer de Tinamït una herramienta aún más accesible! Se puede :ref:`traducir <des_trad>` el interfaz
y la documentación de Tinamït en tu lengua preferida.


Para más información...
-----------------------
.. toctree::
   :maxdepth: 1
   Desarrollar Envolturas MDS <des_mds>
   Desarrollar Envolturas BF <des_bf>
   Contribuir traducciones <des_trad>