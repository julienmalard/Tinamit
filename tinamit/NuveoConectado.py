from Modelo import Modelo
from NuevoMDS import generar_mds

from tinamit.NuevoBF import EnvolturaBF


class SuperConectado(Modelo):
    """

    """

    def __init__(símismo):
        """

        """
        símismo.modelos = {}

        super().__init__(nombre="SuperConectado")

    def estab_modelo(símismo, modelo):
        """

        :param modelo:
        :type modelo: Modelo

        """

        símismo.modelos[modelo.nombre] = modelo

        símismo.variables[modelo.nombre] = modelo.variables

    def cambiar_vals(símismo, valores):
        """

        :param valores:
        :type valores: dict

        """

        for nombre_mod, vals in valores.items():
            símismo.modelos[nombre_mod].cambiar_vals(valores=vals)

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso: int

        """

        for mod in símismo.modelos.values():
            mod.incrementar(paso=paso)

    def leer_vals(símismo):
        """

        """
        for mod in símismo.modelos.values():
            mod.leer_vals()

    def iniciar_modelo(símismo):
        """

        """

        for mod in símismo.modelos.values():
            mod.iniciar_modelo()


class Conectado(SuperConectado):
    """

    """
    def __init__(símismo):

        símismo.mds = None
        símismo.bf = None

        super().__init__()

    def estab_mds(símismo, archivo_mds):
        """

        :param archivo_mds:
        :type archivo_mds: str

        """

        modelo_mds = generar_mds(archivo=archivo_mds)

        símismo.estab_modelo(modelo=modelo_mds)

        símismo.mds = modelo_mds

    def estab_bf(símismo, archivo_bf):
        """

        :param archivo_bf:
        :type archivo_bf: str

        """

        modelo_bf = EnvolturaBF(archivo=archivo_bf)

        símismo.estab_modelo(modelo=modelo_bf)

        símismo.bf = modelo_bf
