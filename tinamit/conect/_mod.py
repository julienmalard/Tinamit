import threading
from warnings import warn as avisar

import numpy as np

from tinamit.config import _
from tinamit.envolt.bf import gen_bf
from tinamit.envolt.mds import gen_mds
from tinamit.mod import Modelo
from tinamit.mod.corrida import Rebanada
from tinamit.unids.conv import convertir
from ._conex import Conex, ConexionesVars
from ._vars import VariablesConectado


class SuperConectado(Modelo):
    """
    Esta clase representa el más alto nivel posible de modelo conectado. Tiene la función muy útil de poder conectar
    instancias de sí misma, así permitiendo la conexión de números arbitrarios de modelos anidados.
    """

    def __init__(símismo, modelos, nombre='SuperConectado'):
        símismo.modelos = _ModelosConectados(modelos)
        símismo.conexiones = ConexionesVars()

        super().__init__(variables=VariablesConectado(símismo.modelos), nombre=nombre)

    def conectar_vars(símismo, var_fuente, var_recip, modelo_fuente=None, modelo_recip=None, conv=None):
        modelo_fuente = símismo._mod_de_var(var_fuente) if modelo_fuente is None else símismo.modelos[modelo_fuente]
        modelo_recip = símismo._mod_de_var(var_recip) if modelo_recip is None else símismo.modelos[modelo_recip]

        var_fuente = modelo_fuente.variables[var_fuente]
        var_recip = modelo_recip.variables[var_recip]

        símismo.conexiones.agregar(
            Conex(var_fuente, modelo_fuente, var_recip, modelo_recip, conv=conv)
        )

    def desconectar_vars(símismo, var_fuente, modelo_fuente, modelo_recip=None, var_recip=None):
        símismo.conexiones.quitar(var_fuente, modelo_fuente, modelo_recip, var_recip)

    def cerrar(símismo):
        for m in símismo.modelos:
            m.cerrar()

    def paralelizable(símismo):
        return all(m.paralelizable() for m in símismo.modelos)

    def unidad_tiempo(símismo):

        unids = list({m.unidad_tiempo() for m in símismo.modelos})
        factores_conv = [1]
        factores_conv[0] = 1
        for u in unids[1:]:
            # Intentar convertir la unidad del submodelo a la unidad de base
            factores_conv.append(convertir(de=unids[0], a=u))
        factores_conv = np.array(factores_conv)
        factores_conv = np.divide(factores_conv, factores_conv.min())

        facts_conv_ent = np.round(factores_conv)
        if not np.array_equal(facts_conv_ent, factores_conv):
            # Si todos los factores no son números enteros, tendremos que aproximar.
            avisar(
                _('Las unidades de tiempo de los modelos ({}) no tienen denominator común. Se aproximará la '
                  'conversión.').format(', '.join(unids))
            )

        return next(u for u, c in zip(unids, factores_conv) if c == 1)

    def iniciar_modelo(símismo, corrida):
        super().iniciar_modelo(corrida)

        for m in símismo.modelos:
            m.iniciar_modelo(corrida)

        símismo._intercambiar_vars()
        corrida.actualizar_res()

    def incrementar(símismo, rebanada):
        def incr_mod(mod, d, reb):
            try:
                mod.incrementar(reb)
            except BaseException as e:
                d[str(mod)] = e
                raise

        # Un diccionario para comunicar errores
        dic_err = {str(x): False for x in símismo.modelos}

        # Un hilo para cada modelo
        l_hilo = [threading.Thread(
            name='hilo_%s' % str(mod),
            target=incr_mod,
            args=(mod, dic_err, Rebanada(
                n_pasos=símismo.corrida.t.pasos_avanzados(mod.unidad_tiempo()),
                resultados=rebanada.resultados[str(mod)],
            )))
            for mod in símismo.modelos
        ]

        # Empezar los hilos al mismo tiempo
        for hilo in l_hilo:
            hilo.start()

        # Esperar que los dos hilos hayan terminado
        for hilo in l_hilo:
            hilo.join()

        # Verificar si hubo error
        for mod, err in dic_err.items():
            if err:
                raise ChildProcessError(_('Hubo error en el modelo "{m}": {e}').format(m=mod, e=err))

        símismo._intercambiar_vars()

    def cambiar_vals(símismo, valores):
        for mod in símismo.modelos:
            mod.cambiar_vals({vr: vl for vr, vl in valores.items() if vr in mod.variables})

    def _mod_de_var(símismo, var):
        return next(m for m in símismo.modelos if var in m.variables)

    def _intercambiar_vars(símismo):
        for c in símismo.conexiones:  # para hacer: por modelo para conexión más rápida
            val_fuente = c.var_fuente.obt_val()

            var_recip = c.modelo_recip.variables[c.var_recip]
            c.modelo_recip.cambiar_vals({str(var_recip): val_fuente * c.conv})


class Conectado(SuperConectado):
    """
    Un modelo que conecta un :class:`~tinamit.envolt.mds.ModeloDS` con un
    :class:`~tinamit.envolt.bf._envolt.ModeloBF`.
    """

    def __init__(símismo, bf, mds, nombre='conectado'):
        símismo.bf = gen_bf(bf)
        símismo.mds = gen_mds(mds) if isinstance(mds, str) else mds

        super().__init__([símismo.bf, símismo.mds], nombre=nombre)

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


class _ModelosConectados(object):
    def __init__(símismo, modelos):
        símismo._modelos = {str(m): m for m in modelos}
        if len(símismo._modelos) != len(modelos):
            raise ValueError(_('Los modelos conectados deben todos tener nombres distintos.'))

    def __iter__(símismo):
        for m in símismo._modelos.values():
            yield m

    def __getitem__(símismo, itema):
        return símismo._modelos[str(itema)]
