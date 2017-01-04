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
        :type archivo:
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

    def cambiar_vals(símismo, valores):
        pass

    def incrementar(símismo, paso):
        pass

    def leer_vals(símismo):
        pass

    def iniciar_modelo(símismo):
        pass


class ClaseModeloBF(object):
    def __init__(símismo):
        pass

    def cambiar_vals(símismo, valores):
        pass

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso:

        """
        raise NotImplementedError

    def leer_vals(símismo):
        pass

    def iniciar_modelo(símismo):
        """

        """
        raise NotImplementedError