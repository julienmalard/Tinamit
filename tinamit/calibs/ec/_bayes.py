import numpy as np

from tinamit.calibs._utils import calc_máx_trz
from tinamit.calibs.ec import CalibradorEc
from tinamit.config import _

try:
    import pymc3 as pm
except ImportError:  # pragma: sin cobertura
    pm = None


class CalibradorEcBayes(CalibradorEc):
    """
    Calibrador de ecuaciones con inferencia bayesiana.
    """

    def calibrar(
            símismo, bd, lugar=None, líms_paráms=None, ops=None, corresp_vars=None, ord_niveles=None, jerárquico=True
    ):
        """
        Efectua una calibración bayesiana para cada lugar en ``Lugar`` según los datos en ``bd``.

        Parameters
        ----------
        bd: BD
            La base de datos con observaciones para los variables en la ecuación.
        lugar: Lugar
            El lugar cuyos sublugares hay que calibrar; si es ``None`` se calibrará la ecuación con todos
            los datos en ``bd`` sin tener su lugar en cuenta.
        líms_paráms: list
            Límites teoréticos para los parámetros.
        ops: dict
            Opciones que se pasarán directamente a la función de calibración.
        corresp_vars: dict
            Diccionario de correspondencia entre los nombres de los variables en ``bd`` y sus nombres en la ecuación.
        ord_niveles: list
            Desambiguación del orden de niveles.
        jerárquico: bool
            Si empleamos inferencia bayesiana jerárquica o normal.

        Returns
        -------
        dict
            Diccionario con las calibraciones de cada lugar.
        """

        # Si no tenemos PyMC3, no podemos hacer inferencia bayesiana.
        if pm is None:
            raise ImportError(_('Debes instalar PyMC3 para poder hacer calibraciones con inferencia bayesiana.'))

        líms_paráms = símismo._gen_líms_paráms(líms_paráms)

        # Leer los variables de la ecuación.
        vars_x, var_y = símismo._extraer_vars()
        # Todas las observaciones
        obs = símismo._obt_datos(bd, vars_interés=vars_x + [var_y], corresp_vars=corresp_vars)
        obs = obs.dropna('n', how='any')

        if lugar is None:
            # Si no hay lugares, generar y calibrar el modelo de una vez.
            mod_bayes = símismo.ec.gen_mod_bayes(
                líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                binario=False, aprioris=None, nv_jerarquía=None
            )

            return _calibrar_mod_bayes(mod_bayes, paráms=list(símismo.paráms), ops=ops)

        # Si hay distribución geográfica, es un poco más complicado.
        if jerárquico:
            # Si estamos implementando un modelo jerárquico...

            ord_niveles = lugar.ord_niveles.resolver(ord_niveles)
            lugs = [lg for lg in lugar.lugares() if lg.nivel in ord_niveles]
            primer_nivel = ord_niveles[0]
            obs = obs.where(obs[_('lugar')].isin([
                h.cód for x in lugar.lugares(nivel=primer_nivel) for h in x
            ]), drop=True)

            # Primero, crear una lista de las relaciones jerárquicas, el cual se necesita para crear el modelo
            # jerárquico bayes.
            nvs_jerarq = [[lugar]]
            while len(lugs):
                for lug in nvs_jerarq[-1]:
                    lugs.remove(lug)
                lgs_nv = [lug for lug in lugs if lugar.pariente(lug) in nvs_jerarq[-1]]
                if len(lgs_nv):
                    nvs_jerarq.append(lgs_nv)
            for í, nv in enumerate(nvs_jerarq):
                nv[:] = [
                    lg for lg in nv
                    if (obs[_('lugar')].isin([x.cód for x in lg.lugares()]).sum()
                        and ((í == len(nvs_jerarq) - 1) or any(
                                lg is lugar.pariente(x, ord_niveles) for x in nvs_jerarq[í + 1]))
                        )
                ]
            í_nv_jerarquía = []
            for í, nv in enumerate(nvs_jerarq[1:]):
                í_nv_jerarquía.append([nvs_jerarq[í].index(lugar.pariente(lg, ord_niveles=ord_niveles)) for lg in nv])

            í_datos = np.array(
                [next(i for i, lg in enumerate(nvs_jerarq[-1]) if x == lg.cód or
                      any(p == lg for p in lugar.pariente(x, ord_niveles=ord_niveles, todos=True))) for x in
                 obs[_('lugar')].values.tolist()
                 ]
            )
            # Generar el modelo bayes
            mod_bayes_jrq = símismo.ec.gen_mod_bayes(
                líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                aprioris=None, binario=False, nv_jerarquía=í_nv_jerarquía,
                í_datos=í_datos
            )
            prms_extras = [
                'mu_{p}_nv_{í}'.format(í=í_nv, p=p) for í_nv in range(len(nvs_jerarq) - 1) for p in símismo.paráms
            ]

            # Calibrar
            res_calib = _calibrar_mod_bayes(
                mod_bayes_jrq, paráms=símismo.paráms + prms_extras, ops=ops
            )

            # Formatear los resultados
            resultados = {}
            for i, nv in enumerate(nvs_jerarq):
                for j, lg in enumerate(nv):
                    if i == (len(nvs_jerarq) - 1):
                        res_lg = {p: {ll: v[..., j] for ll, v in res_calib[p].items()} for p in símismo.paráms}
                    else:
                        res_lg = {
                            p: {ll: v[..., j] for ll, v in res_calib['mu_{}_nv_{}'.format(p, i)].items()}
                            for p in símismo.paráms
                        }
                    resultados[lg.cód] = res_lg

        else:
            # Si no estamos haciendo un modelo jerárquico, hay que calibrar cada lugar individualmente.

            # Efectuar las calibraciones para todos los lugares.
            resultados = {}
            sub_lugs = list(lugar.lugares())
            sub_lugs.remove(lugar)

            for lg in sub_lugs:
                obs_lg = obs.where(obs['lugar'].isin([x.cód for x in lg.lugares()]), drop=True)

                if len(obs_lg['n']):
                    mod_bayes = símismo.ec.gen_mod_bayes(
                        líms_paráms=líms_paráms, obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y],
                        binario=False, aprioris=None, nv_jerarquía=None
                    )
                    resultados[lg.cód] = _calibrar_mod_bayes(
                        mod_bayes=mod_bayes, paráms=símismo.paráms, obs=obs_lg, ops=ops
                    )
        return resultados


# Unas funciones auxiliares
def _calibrar_mod_bayes(mod_bayes, paráms, obs=None, vars_compartidos=None, ops=None):
    """
    Esta función calibra un modelo bayes.

    Parameters
    ----------
    mod_bayes: pm.Modelo
        El modelo para calibrar.
    paráms: list[str]
        Una lista de los nombres de los parámetros de interés para sacar de la traza del modelo.
    obs: dict
        Base de datos observados.
    vars_compartidos: dict
        Un diccionario con los variables compartidos Theano en los cuales podemos poner nuevas observaciones.
    ops: dict
        Opciones adicionales para pasar a pm.Modelo.sample.

    Returns
    -------

    """

    # El diccionario de opciones adicionales.
    if ops is None:
        ops = {}

    # Si hay variables de datos compartidos, poner los nuevos datos.
    if vars_compartidos is not None:
        for var, var_pymc in vars_compartidos.items():
            var_pymc.set_value(obs[var])

    # Crear el diccionarion de argumentos
    ops_auto = {
        'tune': 1000,
        'nuts_kwargs': {'target_accept': 0.90}
    }
    ops_auto.update(ops)

    # Efectuar la calibración
    with mod_bayes:
        t = pm.sample(**ops_auto)

    # Devolver los datos procesados
    return _procesar_calib_bayes(t, paráms=paráms)


def _procesar_calib_bayes(traza, paráms):
    """
    Procesa los resultados de una calibración bayes. Con base en la traza PyMC3, calcula el punto de probabilidad más
    alta para cada parámetro de interés.

    Parameters
    ----------
    traza: pm.Trace
        La traza PyMC3.
    paráms: list
        La lista de parámetros de interés.

    Returns
    -------
    dict
        Los resultados procesados.
    """

    # El diccionario para los resultados
    d_máx = {}
    d_prom = {}

    # Calcular el punto de probabilidad máxima
    for p in paráms:
        # Para cada parámetro...

        dims = traza[p].shape
        if len(dims) == 1:
            d_máx[p] = calc_máx_trz(traza[p])
            d_prom[p] = np.mean(traza[p])
        elif len(dims) == 2:
            d_máx[p] = np.empty(dims[1])
            d_prom[p] = np.empty(dims[1])
            for e in range(dims[1]):
                d_máx[p][e] = calc_máx_trz(traza[p][:, e])
                d_prom[p][e] = np.mean(traza[p][:, e])
        else:
            raise ValueError

    # Devolver los resultados procesados.
    return {p: {'val': d_prom[p], 'cumbre': d_máx[p], 'dist': traza[p]} for p in paráms}
