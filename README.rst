.. image:: tinamit/Interfaz/Imágenes/LogoCent.png
   :scale: 80%
   :alt: Logo muy bonito. :)

.. image:: https://badge.fury.io/py/tinamit.svg
   :target: https://badge.fury.io/py/tinamit

.. image:: https://travis-ci.org/julienmalard/Tinamit.svg?branch=master
   :target: https://travis-ci.org/julienmalard/Tinamit

.. image:: https://ci.appveyor.com/api/projects/status/3s1ppuilm0vioa3p/branch/master?svg=true
   :target: https://ci.appveyor.com/project/julienmalard/tinamit

.. image:: https://coveralls.io/repos/github/julienmalard/Tinamit/badge.svg?branch=master
   :target: https://coveralls.io/github/julienmalard/Tinamit?branch=master

.. image:: https://api.codacy.com/project/badge/Grade/bf248090bd464a0898f637b5ca56d185
   :alt: Codacy
   :target: https://app.codacy.com/app/julienmalard/Tinamit?utm_source=github.com&utm_medium=referral&utm_content=julienmalard/Tinamit&utm_campaign=badger
   
.. image:: https://api.codeclimate.com/v1/badges/cd1b1bf43ee40c270604/maintainability
   :target: https://codeclimate.com/github/julienmalard/Tinamit/maintainability
   :alt: Mantenimiento del código

Tinamit
=======
Programa para conectar modelos socioeconómicos (dinámicas de los sistemas) con modelos biofísicos.

Tinamit permite la conexión rápida, flexible y reproducible de modelos con:

* Un interfaz (IGU) para los que no quieren escribir código.
* Un libreria (IPA) para las que sí.
* Una estructura fácil para conectar modelos en menos de 10 líneas (en vez de cientos).
* Una estructura transparente para que todos puedan agregar modelos y recursos.
* Apoyo multilingual en el IGU.

Tinamït permite conectar modelos biofísicos con modelos socioeconómicos de dinámicas de los sistemas (EnvolturaMDS).
Es muy útil para proyectos de modelización participativa, especialmente en proyectos de manejo del ambiente.
El interaz gráfico traducible facilita la adopción por comunidades en cualquier parte del mundo.


Instalación
===========
`pip install tinamit`


Uso
===
Es muy sencillo.

.. code-block::

    from tinamit.Conectado import Conectado

    modelo = Conectado()

    modelo.estab_mds('Prueba dll.vpm')
    modelo.estab_bf('Prueba bf.py')

    modelo.conectar(var_mds='Lluvia', var_bf='Lluvia', mds_fuente=False)
    modelo.conectar(var_mds='Bosques', var_bf='Bosques', mds_fuente=True)

    res = modelo.simular(paso=1, t_final=100, nombre_corrida='Corrida_Tinamit')
    print(res)


Autores
=======

* `Julien Malard <https://www.researchgate.net/profile/Julien_Malard>`_; Correo: julien.malard@mail.mcgill.ca
* `محمّد اظہر انعام بیگ <https://www.researchgate.net/profile/Azhar_Baig>`_; Correo: muhammad.baig@mail.mcgill.ca
