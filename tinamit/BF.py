import os
import sys
from importlib import import_module as importar_mod

from tinamit.Modelo import Modelo


class EnvolturaBF(Modelo):
    """
    Esta clase ofrece una envoltura para **TODOS** tipos de modelos biofísicos.

    Modelos biofísicos específicos se implementan por crear una subclase de `~tinamit.BF.ClaseModeloBF` específica
    para ellos.
    """

    def __init__(símismo, archivo):
        """
        Incializar la envoltura.

        :param archivo: El archivo con el
        :type archivo: str

        """

        dir_mod, nombre_mod = os.path.split(archivo)
        sys.path.append(dir_mod)

        módulo = importar_mod(os.path.splitext(nombre_mod)[0])

        try:
            modelo = módulo.Modelo  # type: ClaseModeloBF
        except AttributeError:
            raise AttributeError('El archivo especificado ({}) no contiene una clase llamada Modelo.'.format(archivo))

        if callable(modelo):
            símismo.modelo = modelo()
        else:
            símismo.modelo = modelo

        if not isinstance(símismo.modelo, ClaseModeloBF):
            raise TypeError('El archivo especificado ("{}") contiene una clase llamada Modelo, pero'
                            'esta clase no es una subclase de ClaseModeloBF.'.format(archivo))

        super().__init__(nombre='bf')

        símismo.vars_entrando = símismo.modelo.vars_entrando
        símismo.vars_saliendo = símismo.modelo.vars_saliendo

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo empleada por el modelo.

        :return: La unidad de tiempo (p. ejemplo, 'meses', 'días', etc.
        :rtype: str

        """

        return símismo.modelo.unidad_tiempo

    def inic_vars(símismo):
        """
        Inicializa los variables del modelo biofísico y los conecta al diccionario de variables del modelo.

        """

        # Crear el vínculo
        símismo.modelo.variables = símismo.variables

        # Inicializar los variables del modelo externo.
        símismo.modelo.inic_vars()

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función cambia el valor de variables en el modelo.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """

        símismo.modelo.cambiar_vals(valores=valores)

    def incrementar(símismo, paso):
        """
        Esta función avanza el modelo por un periodo de tiempo especificado en `paso`.

        :param paso: El paso.
        :type paso: int

        """

        símismo.modelo.incrementar(paso=paso)

    def leer_vals(símismo):
        """
        Esta función lee los valores del modelo y los escribe en el diccionario interno de variables.

        """
        símismo.modelo.leer_vals()

    def iniciar_modelo(símismo, **kwargs):
        """
        Inicializa el modelo biofísico interno.

        :param kwargs: Argumentos para pasar al modelo interno.

        """

        símismo.modelo.iniciar_modelo(**kwargs)

    def cerrar_modelo(símismo):
        """
        Cierre el modelo interno.
        """

        símismo.modelo.cerrar_modelo()


class ClaseModeloBF(Modelo):
    """
    Se debe desarrollar una subclase de esta clase para cada tipo modelo biofísico que se quiere volver compatible
    con Tinamit.
    """

    def __init__(símismo):
        """
        Esta función correrá automáticamente con la inclusión de `super().__init__()` en la función `__init__()` de las
        subclases de esta clase.
        """
        super().__init__(nombre='modeloBF')

    def cambiar_vals_modelo_interno(símismo, valores):
        """
        Esta función debe cambiar el valor de variables en el modelo biofísico.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """
        Esta función debe cambiar el valor de variables en el :class:`Modelo`, incluso tomar acciones para asegurarse
        de que el cambio se hizo en el modelo externo, si aplica.

        :param valores: Un diccionario de variables y valores para cambiar, con el formato siguiente:
        >>> {'var1': 10,  'var2': 15,
        >>>    ...
        >>>    }
        :type valores: dict

        """

        raise NotImplementedError

    def leer_vals(símismo):
        """
        Esta función debe leer los variables del modelo desde el modelo externo y copiarlos al diccionario interno
        de variables. Asegúrese que esté *actualizando* el diccionario interno, y que no lo esté recreando, lo cual
        quebrará las conexiones con el modelo conectado.
        """
        raise NotImplementedError

    def iniciar_modelo(símismo, **kwargs):
        """
        Esta función debe preparar el modelo para una simulación.
        
        :param kwargs:
        :type kwargs:
        """

        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Esta función debe cerrar la simulación. No se aplica a todos los modelos biofísicos (en ese caso, usar ``pass``
        ).
        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """
        Esta función debe devolver la unidad de tiempo del modelo biofísico.
        
        :return: La unidad de tiempo del modelo.
        :rtype: str
        """
        raise NotImplementedError

    def inic_vars(símismo):
        """
        Esta función debe iniciar el diccionario interno de variables.
        
        MUY IMPORTANTE: Esta función debe modificar el diccionario que ya existe para símismo.variables, no crear un
        diccionario nuevo.
        Por ejemplo, NO HAGAS:
        |  símismo.variables = {var1: {...}, var2: {...}, ...}

        sino:
        |  símismo.variables[var1] = {...}
        |  símismo.variables[var2] = {...}

        Al no hacer esto, romperás la conección entre los diccionarios de variables de ClaseModeloBF y EnvolturaBF,
        lo cual impedirá después la conexión de estos variables con el modelo DS.

        """

        raise NotImplementedError
