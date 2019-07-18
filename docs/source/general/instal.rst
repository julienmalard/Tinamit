Instalación
===========
La instalación debería ser sencilla. Primero necesitarás `Python 3.6+ <(https://www.python.org/downloads)>`_.
Después, puedes instalar Tinamït en la terminal con:

   :command:`pip install tinamit`

.. note::
   Windows `todavía <https://github.com/pypa/pip/pull/5712>`_ está causando complicaciones con programas no escritos
   en inglés (sí, en 2019). Si encuentras problemas, no hesites en
   `pedir ayuda <https://github.com/julienmalard/Tinamit/issues/new/choose>`_; por eso existe la comunidad.

Si quieres la versión más recién (en desarrollo), puedes obtenerla de GitHub directamente con:

   :command:`pip install git+git://github.com/julienmalard/tinamit.git@master`

.. note::

   Si tienes Windows, es posible que tengas que instalar el ``C++ redistributable`` de
   `aquí <https://support.microsoft.com/es-gt/help/2977003/the-latest-supported-visual-c-downloads>`_.
   Toma la versión terminando en ``…x86.exe`` si tienes Python de 32 bits y en ``…x64.exe`` si tienes **Python**
   (no Windows) de 64 bits. Después, instálalo. Por razones obscuras, ``SciPy``, un paquete requerido por Tinamït,
   no funciona en Windows sin éste.
