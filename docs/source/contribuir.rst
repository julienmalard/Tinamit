Contribuir a Tinamit
====================

.. contents:: Contenido
   :depth: 3

Traducir
--------
¡Siempre querremos traducciones para hacer de Tinamit una herramienta aún más accesible!
El interfaz de Tinamit tiene funcionalidades para la traducción del interfaz sí mismo (el globo).

.. image:: Imágenes/IGU_cabeza_globo.png
   :scale: 100 %
   :align: center
   :alt: Icono de cambio de idiomas de Tinamit.

Allí puedes editar lenguas existentes o agregar nuevas lenguas. Notar que hay un error en la funcionalidad del
interfaz de Python para escribir texto en lenguas indias. Para estas, desafortunademente tienes que escribir tu traducción
en otro programa primero (Word, Notas, etc.) y después copiarla en la caja. Lo siento. (Pero no es culpa mia.)

Para chino, etc. no hay problemas. Hay unas cosas muy raras que pasan con abecedarios que se escriben de la derecha hacia
la izquierda (árabe, hebreo). Estoy trabajando (un día) para resolver eso.

Agregar modelos biofísicos
--------------------------
Cada modelo biofísico en Tinamit necesita una envoltura específica para él. Es por esta envoltura que Tinamit sabrá cómo
controlar el modelo biofísico, cómo leer sus egresos y cómo actualizarlos con los valores del modelo DS. Visto que la gran mayoría
de modelos biofísicos están escritos en lenguas compiladas y por veces oscuras, esta es la parte la más difícil de usar Tinamit.
Lo bueno es que solamente se tiene que hacer una vez por cada tipo de modelo biofísico, y que Tinamit ya viene con algunos
prehechos. Si vas a tener que crear una nueva envoltura para ti, ¡te rogamos que la compartes con todos!

Cómo hacer una nueva envoltura
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
En teoría, es muy fácil. Simplemente tienes que crear una nueva instancia de la clase class:`~tinamit.BF.ClaseModeloBF`
y después implementar allí las funciones siguientes:

* :func:`~tinamit.BF.ClaseModeloBF.__init__`
* :func:`~tinamit.BF.ClaseModeloBF.cambiar_vals_modelo`
* :func:`~tinamit.BF.ClaseModeloBF.incrementar`
* :func:`~tinamit.BF.ClaseModeloBF.leer_vals`
* :func:`~tinamit.BF.ClaseModeloBF.iniciar_modelo`
* :func:`~tinamit.BF.ClaseModeloBF.cerrar_modelo`
* :func:`~tinamit.BF.ClaseModeloBF.obt_unidad_tiempo`
* :func:`~tinamit.BF.ClaseModeloBF.inic_vars`

Puedes escribir tu envoltura en cualquier archivo (hacia no tiene que ser en el código fuente de Tinamit sí mismo).
La subclase incluida es este archivo **debe** llamarse ``Modelo``. Si se llama cualquier otra cosa, no funcionará.

Cómo compartir tu nueva envoltura
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
La manera más fácil (para mi) es que te inscribas en GitHub, creas una nueva rama de Tinamit, le agreges tu nueva envoltura
y después la combinemos con la rama central del proyecto.
La manera más fácil para ti es probablemente mandarme tu nuevo código por correo electrónico (|correo|).

Unos apuntos para cuándo vas a compartir una nueva envoltura:

* Incluir instrucciones, si necesario, para que tus usuarios puedan conseguir el modelo biofísico correspondiente.
* Incluir tantos comentarios como posible en tu envoltura (el código fuente de Tinamit es un ejemplo).
* Se recomienda escribir envolturas en castellano, pero aceptamos envolturas escritas en todos idiomas.

