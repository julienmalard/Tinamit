.. _desarrollo:

Desarrollo de Tinamït
=====================
Tinamït tiene una estructura modular, así que es muy fácil agregar más funcionalidades. En particular, por el desarrollo de envolturas específicas, se puede agregar compatibilidad con varios programas de modelos **de dinámicas de sistemas (DS)** y modelos **biofísicos (BF)**. También se pueden contribuir **traducciones** del interfaz y de la documentación.

Además, Tinamït permite incorporar los resultados de modelos de **predicción climática** en las corridas de modelos apropiados.

Modelos DS
----------
Tinamït queda compatible con modelos escritos con los programas siguientes. Siempre puedes :ref:`escribir más <des_mds>`.

* **Vensim**: Un programa de MDS bastante popular. Desafortunadamente, requiere la versión pagada (DSS) para conectar con Tinamït. Ver su página oficial y la envoltura.
* **Stella**: Otro programa bastante popular. Ver su página oficial aquí. Envoltura todavía en trabajo.

Modelos BF
----------
Cada envoltura agrega compatibilidad con un tipo de modelo biofísico distinto. Siempre puedes :reg:`agregar uno <des_bf>` para tu modelo BF preferido. Por el momento, tenemos:

* **SAHYSMOD**: Un modelo de salinidad de suelos. Ver la documentación completa y la envoltura.
* **DSSAT**: Un modelo de cultivos, que toma en cuenta semilla, clima, suelo y manejo humano. Ver la documentación completa. (Envoltura en trabajo.)

Modelos de Clima
----------------
Tinamït, por el paquete :py:ref:`taqdir`, ofrece la posibilidad de correr análisis de impactos de cambios climáticos.

* **Marksim 5**: 
* **Marksim 3**:
