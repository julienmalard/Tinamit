from tinamit import Modelo
from tinamit.envolt.bf import gen_bf
from tinamit.envolt.mds import gen_mds
from ._conex import Conex, ConexionesVars
from ._vars import VariablesConectado


class SuperConectado(Modelo):

    def __init__(símismo, modelos, nombre='superconectado'):
        símismo.modelos = ModelosConectados(modelos)
        símismo.conexiones = ConexionesVars()
        super().__init__(nombre=nombre)

    def conectar_vars(símismo, var_fuente, modelo_fuente, var_recip, modelo_recip, conv=None):
        símismo.conexiones.agregar(
            Conex(var_fuente, modelo_fuente, var_recip, modelo_recip, conv=conv)
        )

    def desconectar_vars(símismo, var_fuente, modelo_fuente, modelo_recip=None, var_recip=None):
        símismo.conexiones.quitar(var_fuente, modelo_fuente, modelo_recip, var_recip)

    def cerrar(símismo):
        for m in símismo.modelos:
            m.cerrar()

    def paralelizable(símismo):
        return all(m.paralizable for m in símismo.modelos)

    def _gen_vars(símismo):
        return VariablesConectado(símismo.modelos)


class Conectado(SuperConectado):

    def __init__(símismo, bf, mds, nombre='conectado'):

        símismo.bf = gen_bf(bf)
        símismo.mds = gen_mds(mds) if isinstance(mds, str) else mds

        super().__init__([bf, mds], nombre=nombre)

    def conectar(símismo, var_mds, var_bf, mds_fuente, conv=None):
        """
        Una función para conectar variables entre el modelo biofísico y el modelo DS.

        Parameters
        ----------
        var_mds: str
            El nombre del variable en el modelo DS.
        var_bf: str
            El nombre del variable correspondiente en el modelo biofísico.
        mds_fuente: bool
            Si ``True``, el modelo DS es el modelo fuente para la conexión. Sino, será el modelo biofísico.
        conv: float
            El factor de conversión entre los variables.

        """

        # Establecer los variables y modelos fuentes y recipientes.
        modelo_fuente = símismo.mds if mds_fuente else símismo.bf
        var_fuente = var_mds if mds_fuente else var_bf

        modelo_recip = símismo.bf if mds_fuente else símismo.mds
        var_recip = var_bf if mds_fuente else var_mds

        # Llamar la función apropiada de la clase superior.
        símismo.conectar_vars(
            var_fuente=var_fuente, modelo_fuente=modelo_fuente,
            var_recip=var_recip, modelo_recip=modelo_recip, conv=conv
        )

    def desconectar(símismo, var_mds):
        """
        Esta función deshacer una conexión entre el modelo biofísico y el modelo DS. Se especifica la conexión por
        el nombre del variable en el modelo DS.

        Parameters
        ----------
        var_mds: str
            El nombre del variable conectado en el modelo DS.

        """

        # Llamar la función apropiada de la clase superior.
        símismo.desconectar_vars(var_fuente=var_mds, modelo_fuente=símismo.mds)


class ModelosConectados(object):
    def __init__(símismo, modelos):
        símismo._modelos = {str(m): m for m in modelos}
        if len(símismo._modelos) != len(modelos):
            raise ValueError(_('Los modelos conectados deben todos tener nombres distintos.'))

    def __iter__(símismo):
        for m in símismo._modelos.values():
            yield m
