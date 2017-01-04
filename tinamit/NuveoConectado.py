from .Modelo import Modelo
from .NuevoMDS import generar_mds

from tinamit.NuevoBF import EnvolturaBF


class SuperConectado(Modelo):
    """

    """

    def __init__(símismo):
        """

        """
        símismo.modelos = {}

        símismo.conexiones = []

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

    def cerrar_modelo(símismo):
        """

        """

        for mod in símismo.modelos:
            mod.cerrar_modelo()

    def conectar_vars(símismo, dic_vars, modelo_fuente, conv=1):
        """

        :param dic_vars:
        :type dic_vars:
        :param modelo_fuente:
        :type modelo_fuente:
        :param conv:
        :type conv:

        """

        l_modelos = list(símismo.modelos)

        for mod in dic_vars:
            if mod not in símismo.modelos:
                raise ValueError('Nombre de modelo "{}" erróneo.'.format(mod))

        try:
            índ_mod_fuente = l_modelos.index(modelo_fuente)
            modelo_recip = l_modelos[(índ_mod_fuente+1) % 2]
        except ValueError:
            raise ValueError('Nombre de modelo "{}" erróneo.'.format(modelo_fuente))

        var_fuente = dic_vars[modelo_fuente]
        var_recip = dic_vars[modelo_recip]

        dic_conex = {'modelo_fuente': modelo_fuente,
                     'vars': {modelo_recip: var_recip,
                              modelo_fuente: var_fuente
                              },
                     'conv': conv
                     }

        símismo.conexiones.append(dic_conex)

        símismo.modelos[modelo_fuente].vars_egreso.append(var_fuente)
        símismo.modelos[modelo_recip].vars_ingreso.append(var_recip)


        if isinstance(mod, SuperConectado):
            mod

    def desconectar_vars(símismo, var, modelo_fuente):
        """

        :param var:
        :type var:
        :param modelo_fuente:
        :type modelo_fuente:

        """

        for n, conex in enumerate(símismo.conexiones):
            if conex['modelo_fuente'] == modelo_fuente and conex['vars'][modelo_fuente] == var:
                símismo.conexiones.pop(n)


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

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=1):

        dic_vars = {'mds': var_mds, 'bf': var_bf}

        if mds_fuente:
            fuente = 'mds'
        else:
            fuente = 'bf'

        símismo.conectar_vars(dic_vars=dic_vars, modelo_fuente=fuente, conv=conv)
