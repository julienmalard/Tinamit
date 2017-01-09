import os
import sys
from importlib import import_module as importar_mod

from tinamit.Modelo import Modelo


class EnvolturaBF(Modelo):
    """

    """

    def __init__(símismo, archivo):
        """

        :param archivo:
        :type archivo: str

        """

        dir_mod, nombre_mod = os.path.split(archivo)
        sys.path.append(dir_mod)

        módulo = importar_mod(os.path.splitext(nombre_mod)[0])

        try:
            símismo.modelo = módulo.Modelo()
        except AttributeError:
            raise AttributeError('El archivo especificado ({}) no contiene una clase llamada Modelo.'.format(archivo))

        if not isinstance(símismo.modelo, ClaseModeloBF):
            raise AttributeError('El archivo especificado ({}) contiene una clase llamada Modelo, pero'
                                 'esta clase no es una subclase de ClaseModeloBF.'.format(archivo))

        super().__init__(nombre='bf')

        símismo.vars_entrando = símismo.modelo.vars_entrando
        símismo.vars_saliendo = símismo.modelo.vars_saliendo

    def obt_unidad_tiempo(símismo):
        """

        :return:
        :rtype: str

        """

        return símismo.modelo.unidad_tiempo

    def inic_vars(símismo):
        """

        """
        símismo.modelo.variables = símismo.variables

        símismo.modelo.inic_vars()

    def cambiar_vals_modelo(símismo, valores):
        """

        :param valores:
        :type valores:

        """

        símismo.modelo.cambiar_vals(valores=valores)

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso:

        """

        símismo.modelo.incrementar(paso=paso)

    def leer_vals(símismo):
        """

        """
        símismo.modelo.leer_vals()

    def iniciar_modelo(símismo, **kwargs):
        """

        :param kwargs:
        :type kwargs:

        """

        símismo.modelo.iniciar_modelo(**kwargs)

    def cerrar_modelo(símismo):
        """

        """

        símismo.modelo.cerrar_modelo()


class ClaseModeloBF(Modelo):
    """
    Se debe desarrollar una subclase de esta clase para cada tipo modelo biofísico que se quiere volver compatible
    con Tinamit.
    """

    def __init__(símismo):
        """
        Esta función correrá automáticamente con la inclu
        """
        super().__init__(nombre='modeloBF')

    def cambiar_vals_modelo(símismo, valores):
        """

        :param valores:
        :type valores:
        """
        raise NotImplementedError

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso:

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

        :param kwargs:
        :type kwargs:
        """

        raise NotImplementedError

    def cerrar_modelo(símismo):
        """

        """
        raise NotImplementedError

    def obt_unidad_tiempo(símismo):
        """

        :return:
        :rtype: str
        """
        raise NotImplementedError

    def inic_vars(símismo):
        """

        MUY IMPORTANTE: Esta función debe modificar el diccionario que ya existe para símismo.variables, no crear un
        diccionario nuevo.
        Por ejemplo, NO HAGAS:
          símismo.variables = {var1: {...}, var2: {...}, ...}
        sino:
          símismo.variables[var1] = {...}
          símismo.variables[var2] = {...}

        Al no hacer esto, romperás la conección entre los diccionarios de variables de ClaseModeloBF y EnvolturaBF,
        lo cual impedirá después la conexión de estos variables con el modelo DS.

        """
        raise NotImplementedError
