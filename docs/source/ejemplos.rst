Ejemplos
========

Aquí presentamos unos ejemplos del uso de Tinamit, más allá de lo presentado en la sección :doc:`Uso <uso>`.

El código para estos ejemplos también se encuentra en el archivo :file:`Ejemplos` de Tinamit.


Ejemplo muy básico
------------------
También es un ejemplo un poco estúpido. Pero demuestra muy bien cómo funciona Tinamit, y no tienes que instalar
cualquier modelo biofísico externo para que te funcione, así que empecemos con este. ::

    import os
    from tinamit.Conectado import Conectado

    modelo = Conectado()
    directorio = os.path.dirname(__file__)
    modelo.estab_mds(os.path.join(directorio, "Prueba dll.vpm"))
    modelo.estab_bf(os.path.join(directorio, 'Prueba bf.py'))
    modelo.conectar(var_mds='Lluvia', var_bf='var1', mds_fuente=False)
    modelo.simular(paso=1, tiempo_final=100, nombre_corrida='Corrida_Tinamit')
