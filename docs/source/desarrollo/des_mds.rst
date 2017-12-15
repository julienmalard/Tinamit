.. _des_mds:

Agregar programas MDS
=====================
Para poder conectar modelos de dinámicas de sistemas (DS) en Tinamït, el programa DS debe ser compatible con Tinamït.
Este se asegura por escribir una envoltura que controla el programa DS. Lo bueno es que las envolturas para programas
DS en Tinamït funcionan para todos los modelos escritos con el programa. Por ejemplo, la envoltura
:class:`~tinamit.MDS.ModeloVensim` permite conectar cualquier modelo escrito en Vensim con Tinamït.

Cómo crear una nueva envoltura
------------------------------
Si quieres hacer una nueva envoltura para otro tipo de modelo DS, tendrás que hacer una subclase de
:class:`~tinamit.MDS.EnvolturaMDS` e implementar las funciones siguientes:

* :func:`~tinamit.MDS.EnvolturaMDS.obt_unidad_tiempo`: Devuelve la unidad de tiempo del modelo.
* :func:`~tinamit.MDS.EnvolturaMDS.inic_vars`: Incializa el diccionario interno de variables disponibles.
* :func:`~tinamit.MDS.EnvolturaMDS.iniciar_modelo`: Inicializa la simulación.
* :func:`~tinamit.MDS.EnvolturaMDS.cambiar_vals_modelo_interno`: Cambia los valores internos de los variables.
* :func:`~tinamit.MDS.EnvolturaMDS.incrementar`: Avanza el modelo.
* :func:`~tinamit.MDS.EnvolturaMDS.leer_vals`: Lee los egresos del modelo.
* :func:`~tinamit.MDS.EnvolturaMDS.cerrar_modelo`: Cierre el modelo al final de una simulación.

Ver :class:`~tinamit.MDS.ModeloVensim` para un ejemplo.

Cómo conectar tu envoltura con Tinamït
--------------------------------------
Para que Tinamït pueda automáticamente crear la envoltura apropiada cuando un usuario le pasa un archivo de modelo DS,
tienes que decir a Tinamït cuál extensión tienen los archivos de modelo DS que se deben abrir con tu nueva envoltura.
Tendrás que modificar la función :func:`~tinamit.MDS.generar_mds` para incluir la(s) extension(es) para tu nuevo
programa DS. Por ejemplo, para agregar una envoltura para Stella (suponemos que las extensiones serán
``.stmx`` o ``.stm``), cambiamos el código así::

    # Crear la instancia de modelo apropiada para la extensión del archivo.
    if ext == '.vpm':
        # Modelos Vensim
        return ModeloVensim(archivo)

    # Agregar este código
    elif ext == '.stmx' or ext == '.stm':
        # Modelos Stella
        return ModeloStella(archivo)
    # Fin del nuevo código

    else:
        # Agregar otros tipos de modelos DS aquí.

        # Mensaje para modelos todavía no incluidos en Tinamit.
        raise ValueError()


Leer egresos
------------
Si quieres poder generar mapas, etc. con el egreso de tu modelo DS, tendrás que decir a Tinamït cómo leer el archivo
de egresos de tu modelo DS. Al momento puede leer archivos ``.vdf`` de Vensim y ``.csv``. Si tu modelo DS genera otro
formato raro, puedes modificar el código de :func:`~tinamit.MDS.leer_egr_mds` para que Tinamït lo pueda leer también.

Cambios climáticos
------------------
Al contrario de envolturas de modelos biofísicos, modelos DS no necesitan cualquier modificación para poder conectar
con variables climáticos. El usuario simplemente debe llamar la función
:func:`~tinamit.Modelo.Modelo.conectar_var_clima` con el nombre del variable
climático en su modelo DS y el nombre estándar del variable climático correspondiente en Tinamït.
