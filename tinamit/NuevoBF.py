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

    def cerrar_modelo(símismo):
        pass

    def obt_unidades_tiempo(símismo):
        """

        :return:
        :rtype: str

        """

        return símismo.modelo.obt_unidades_tiempo()

    def inic_vars(símismo):
        """

        """
        símismo.modelo.inic_vars()

        símismo.variables = símismo.modelo.variables

    def cambiar_vals(símismo, valores):
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

        pass

    def iniciar_modelo(símismo, **kwargs):
        """

        :param kwargs:
        :type kwargs:

        """
        símismo.modelo.iniciar_modelo(**kwargs)


class ClaseModeloBF(Modelo):
    """

    """

    def __init__(símismo):
        """

        """
        pass

    def cambiar_vals(símismo, valores):
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

        """
        raise NotImplementedError

    def iniciar_modelo(símismo):
        """

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """

        """
        raise NotImplementedError

    def obt_unidades_tiempo(símismo):
        """

        :return:
        :rtype: str
        """
        raise NotImplementedError

    def inic_vars(símismo):
        """

        """
        raise NotImplementedError
