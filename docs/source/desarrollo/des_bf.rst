.. _des_bf:

Agregar modelos biofísicos
==========================
Cada modelo biofísico en Tinamït necesita una envoltura específica para él. Es por esta envoltura que Tinamït sabrá cómo
controlar el modelo biofísico, cómo leer sus egresos y cómo actualizarlos con los valores del modelo DS. Visto que la gran mayoría
de modelos biofísicos están escritos en lenguas compiladas y por veces oscuras, esta es la parte la más difícil de usar Tinamït.
Lo bueno es que solamente se tiene que hacer una vez por cada *tipo* de modelo biofísico, y que Tinamït ya viene con algunos
prehechos. Si vas a tener que crear una nueva envoltura para ti, por favor no dudes en compartirla.

Cómo crear una nueva envoltura
------------------------------
En teoría, es muy fácil. Simplemente tienes que crear una nueva subclase de la clase :class:`~tinamit.BF.ModeloBF`
y después implementar allí las funciones que faltan. Si tienes un modelo que no se comporte tan bien, también puedes
usar como plantilla una de las subclases de :class:`~tinamit.BF.ModeloBF` que ya hemos escrito para para
facilitarte la vida. (Fue un placer.)

¿Cómo escojo la mejor plantilla?
--------------------------------
Para ayudarte a decidir cuál plantilla es mejor para ti, consulta el cuestionario siguiente.

#. Mi modelo avanza con el **mismo paso que la precisión de sus egresos e ingresos**. Por ejemplo, tengo un modelo de
   poblaciones de insectos que puede avanzar con un paso de 1 mes y me da las poblaciones. Entonces, utilizar la
   plantilla estándar :class:`~tinamit.BF.ModeloBF`. Más detalles
   :ref:`abajo <plantilla_modbf>`.
#. Mi modelo avanza con un paso **superior a la precisión de sus egresos o ingresos**. Por ejemplo, mi modelo de
   salinidad de los suelos avanza por un paso mínimo de 1 año, pero después me da predicciones de salinidad distintas
   para dos estaciones de 6 meses cada una. Entonces, utilizar :class:`~tinamit.BF.ModeloImpaciente`. Más detalles
   :ref:`abajo <plantilla_modimp>`.
#. Mi modelo avanza con un **paso variable**. Por ejemplo, mi modelo de cultivos corre hasta la cosecha, la cual varía
   según el cultivo y el clima. Entonces, utilizar :class:`~tinamit.BF.ModeloFlexible`. Más detalles
   :ref:`abajo <plantilla_modflex>`.

Si todavía no estás segura, empieza con :class:`~tinamit.BF.ModeloBF`. Saberás que no fue la buena decisión por quedarte
muy confundida muy pronto.

.. note::

   Puedes escribir tu envoltura en cualquier archivo (hacia no tiene que ser en el código fuente de Tinamït sí mismo).
   La subclase incluida es este archivo, o su implementación final, **debe** llamarse ``Modelo``. Si se llama
   cualquier otra cosa, no funcionará.

.. note::

   En teoría puedes implementar cualquier modelo con la plantilla estándar (todas las otras son subclases de esta),
   pero las otras te ahorarán mucho tiempo para modelos con pasos complicados.

.. _plantilla_modbf:

Plantilla estándar (ModeloBF)
-----------------------------
Esta plantilla es la más sencilla (y todas las otras son subclases de esta). Deberás implementar las funciones
siguientes en una subclase de esta plantilla.

* :func:`~tinamit.BF.ModeloBF.unidad_tiempo`: Devuelve la unidad de tiempo del modelo.
* :func:`~tinamit.BF.ModeloBF._inic_dic_vars`: Incializa el diccionario interno de variables disponibles.
* :func:`~tinamit.BF.ModeloBF.iniciar_modelo`: Inicializa la simulación.
* :func:`~tinamit.BF.ModeloBF._cambiar_vals_modelo_interno`: Cambia los valores internos de los variables.
* :func:`~tinamit.BF.ModeloBF.incrementar`: Avanza el modelo.
* :func:`~tinamit.BF.ModeloBF.leer_vals`: Lee los egresos del modelo.
* :func:`~tinamit.BF.ModeloBF.cerrar_modelo`: Cierre el modelo al final de una simulación.

.. _plantilla_modimp:

Plantilla ModeloImpaciente
--------------------------
Un ejemplo del uso de esta plantilla es la envoltura para el modelo de salinidad de suelos SAHYSMOD. La plantilla maneja el
control del modelo, incluso su simulación y la lectura retrospectiva de valores de variables para distintos meses o
estaciones, de manera automática. Simplemente debes implementar las funciones siguientes en una subclase:

* :func:`~tinamit.BF.ModeloImpaciente.iniciar_modelo`: Inicializa la simulación.
* :func:`~tinamit.BF.ModeloImpaciente.cerrar_modelo`: Cierre el modelo al final de una simulación.
* :func:`~tinamit.BF.ModeloImpaciente._inic_dic_vars`: Incializa el diccionario interno de variables disponibles.
* :func:`~tinamit.BF.ModeloImpaciente.avanzar_modelo`: Avanza la simulación del paso mínimo del modelo (por ejemplo,
  avanzará un modelo anual de 1 año, aunque este de resultados con una precisión de 1 mes). No te preoccupes, Tinamït
  arreglará todo.
* :func:`~tinamit.BF.ModeloImpaciente.leer_archivo_vals_inic`: Lee un archivo con valores inciales para la simulación.
* :func:`~tinamit.BF.ModeloImpaciente.leer_archivo_egr`: Le un archivo de los egresos de una simulación.
* :func:`~tinamit.BF.ModeloImpaciente.escribir_archivo_ingr`: Escribe un archivo de ingresos para el modelo, basado en
  los valores de los variables internos actuales.

Un ejemplo sería la envoltura para SAHYSMOD, :class:`~tinamit.EnvolturaBF.en.SAHYSMOD.SAHYSMOD_Wrapper`.

.. _plantilla_modflex:

Plantilla ModeloFlexible
------------------------
Un ejemplo de esta plantilla sería la envoltura para el modelo de cultivos DSSAT. Simplemente debes implementar
las funciones siguientes en una subclase:

.. warning::
   Esta plantilla todavía está en desarrollo.

* :func:`~tinamit.BF.ModeloFlexible.iniciar_modelo`: Inicializa la simulación.
* :func:`~tinamit.BF.ModeloFlexible.cerrar_modelo`: Cierre el modelo al final de una simulación.
* :func:`~tinamit.BF.ModeloFlexible._inic_dic_vars`: Incializa el diccionario interno de variables disponibles.
* :func:`~tinamit.BF.ModeloFlexible.mandar_modelo`: Avanza la simulación.
* :func:`~tinamit.BF.ModeloFlexible.leer_archivo_vals_inic`: Lee un archivo con valores inciales para la simulación.
* :func:`~tinamit.BF.ModeloFlexible.leer_archivo_egr`: Le un archivo de los egresos de una simulación.
* :func:`~tinamit.BF.ModeloFlexible.escribir_archivo_ingr`: Escribe un archivo de ingresos para el modelo, basado en
  los valores de los variables internos actuales.

Un ejemplo sería la envoltura para DSSAT, :class:`~tinamit.EnvolturaBF.es.DSSAT.envoltDSSAT`.

Modelos externos
----------------
La casi totalidad de las envolturas BF van a necesitar un modelo externo a Tinamït. Se recomienda incluir un enlace
al donde se puede descargar el modelo externo en los comentarios, si posible.

Otro asunto es que cada usuario de tu envoltura estará utilizando una computadora diferente, con el modelo externo
guardado en lugar distinto. Por eso no te recomiendo hacer algo así::

    class MiEnvoltura(EnvolturaBF):
         ubic_modelo = 'C:\Yo\MisDocumentos\MisPropiasCarpetas\Que\Tú\No\Tienes\Modelo.exe'
         def init(símismo):
            ...

Por razones obvias, aunque todo funcione bien para ti, otros posiblemente tendrán dificultades con tu envoltura.
Por eso Tinamït te propone una función especial, ``tinamit.obt_val_config()``, que pide al usuario el directorio
del modelo en *su* computadora la primera vez que emplea tu envoltura y despúes lo guarda en un archivo local para uso
futuro. Se emplea así::

    from tinamit import obt_val_config
    class MiEnvoltura(EnvolturaBF):

         def __init__(símismo, ubic_modelo=None):
             if ubic_modelo is None:
                 ubic_modelo = obt_val_config('exe_dssat', mnsj='Especificar la ubicación de la instalación de'
                                              'tu modelo "DSSAT".')
             ...

Así, si ya existe un valor para ``exe_dssat`` en la configuración local de Tinamït, tomará este valor. Sino, pedirá
al usuario que se lo entregue.

Cambios climáticos
------------------
Si tu modelo incluye variables climáticos, deberías considerar escribirlo para que pueda comunicar con las
funcionalidades de cambios climáticos de Tinamït. Esto permitirá que Tinamït actualize los valores de estos variables
según el escenario climático escogido por el usuario.

Cuando un usuario corre un modelo con un escenario climático, cada modelo conectado se conectará automáticamente, por
su atributo ``.lugar``, con un objeto :class:`~tinamit.Geog.Geog.Lugar`. Si tu modelo requiere datos climáticos con la
**misma precisión que su paso**, simplemente puedes llamar la función :func:`~tinamit.Modelo.Modelo.conectar_var_clima`
en su método :func:`~tinamit.BF.ModeloBF.__init__`. Por ejemplo, en la envoltura de SAHYSMOD::

   self.conectar_var_clima(var='Pp - Rainfall', var_clima='Precipitación', combin='total')

Esta comanda conecta el variable interno ``Pp - Rainfall`` de la envoltura SAHYSMOD con el variable climático
``Precipitación``. En cada paso, Tinamït actualizará este variable con el valor ``total`` de precipitación en cada
paso de la simulación para el escenario climático apropiado. Chévere, ¿no?

El parámetro ``var`` es el nombre de este variable en tu envoltura. Puede ser lo que quieres, en el idioma que quieres.
La opciones actuales para variables climáticos (``var_clima``) incluyen:

* ``Precipitación`` : mm
* ``Radiación solar`` : MJ / m2 / día
* ``Temperatura máxima`` : grados C
* ``Temperatura promedia`` : grados C
* ``Temperatura mínima`` : grados C

.. note::
   ``Combin`` puede ser ``prom`` (calculará el promedio de este variable climático por el periodo deseado) o ``total``
   (calculará el total, como para lluvia). Si no se especifica, se supondrá ``total`` para ``Precipitación`` y ``prom``
   para todos los otrs variables climáticos.

Si, al contrario, tu modelo necesita variables climáticos **con un paso distinto del suyo** (por ejemplo, un modelo de
cultivos necesita que los variables climáticos diarios se escriben en un archivo separado antes de empezar la
simulación), lo tendrás que implementar en :func:`~tinamit.BF.ModeloBF.iniciar_modelo`. Puedes acceder los variables
climáticos que quieres con el método :func:`~tinamit.Geog.Geog.Lugar.devolver_datos` de ``símismo.lugar``.

