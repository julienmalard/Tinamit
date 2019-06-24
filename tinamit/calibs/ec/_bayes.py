import numpy as np

from tinamit.calibs._utils import calc_máx_trz
from tinamit.calibs.ec import CalibradorEc
from tinamit.config import _

try:
    import pymc3 as pm
except ImportError:  # pragma: sin cobertura
    pm = None


class CalibradorEcBayes(CalibradorEc):

    def calibrar(
            símismo, bd, lugar=None, líms_paráms=None, ops=None, corresp_vars=None, ord_niveles=None, jerárquico=True
    ):

        # Si no tenemos PyMC3, no podemos hacer inferencia bayesiana.
        if pm is None:
            raise ImportError(_('Debes instalar PyMC3 para poder hacer calibraciones con inferencia bayesiana.'))

        líms_paráms = símismo._gen_líms_paráms(líms_paráms)

        # Leer los variables de la ecuación.
        vars_x, var_y = símismo._extraer_vars()

        # Todas las observaciones
        obs = símismo._obt_datos(bd, vars_interés=vars_x + [var_y], corresp_vars=corresp_vars)

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

            # Primero, crear una lista de las relaciones jerárquicas, el cual se necesita para crear el modelo
            # jerárquico bayes.
            lugs = lugar.lugares()
            nvs_jerarq = [[lugar]]
            while len(lugs):
                for lug in nvs_jerarq[-1]:
                    lugs.remove(lug)
                lgs_nv = [lug for lug in lugs if lugar.pariente(lug) in nvs_jerarq[-1]]
                print(lgs_nv)
                if len(lgs_nv):
                    nvs_jerarq.append(lgs_nv)
            print([[y.cód for y in x] for x in nvs_jerarq])
            for í, nv in enumerate(nvs_jerarq):
                nv[:] = [
                    lg for lg in nv
                    if (obs['lugar'].isin([x.cód for x in lg.lugares()]).sum()
                        and ((í == len(nvs_jerarq) - 1) or any(
                                lg is lugar.pariente(x, ord_niveles) for x in nvs_jerarq[í + 1]))
                        )
                ]

            print([[y.cód for y in x] for x in nvs_jerarq])

            í_nv_jerarquía = []
            for í, nv in enumerate(nvs_jerarq[1:]):
                for lg in nv:
                    print(lg.cód, lugar.pariente(lg).cód)
                print([x.cód for x in nvs_jerarq[í]])
                í_nv_jerarquía.append([nvs_jerarq[í].index(lugar.pariente(lg)) for lg in nv])

            print(í_nv_jerarquía)

            # Generar el modelo bayes
            mod_bayes_jrq = símismo.ec.gen_mod_bayes(
                líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                aprioris=None, binario=False, nv_jerarquía=í_nv_jerarquía[::-1],
            )
            var_res_lugares = {}
            for lg in lugares:
                if lg in nv_jerarquía[-1]:
                    var_res_lugares[lg] = nv_jerarquía[-1].index(lg)
                else:
                    for í, nv in enumerate(nv_jerarquía[1::-1]):
                        id_nv = lg
                        while id_nv is not None:
                            id_nv = jerarquía[id_nv]
                            if id_nv in nv:
                                var_res_lugares[lg] = (í + 1, nv.index(id_nv))
                                break
                        if lg in var_res_lugares:
                            break

            prms_extras = list({
                'mu_{p}_nv_{í}'.format(p=p, í=x[0]) for x in set(var_res_lugares.values()) if isinstance(x, tuple)
                for p in símismo.paráms
            })

            # Calibrar
            res_calib = _calibrar_mod_bayes(
                mod_bayes_jrq, paráms=símismo.paráms + prms_extras, ops=ops
            )

            # Formatear los resultados
            resultados = {}
            for lg in lugares:
                ubic_res = var_res_lugares[lg]

                if isinstance(ubic_res, int):
                    resultados[lg] = {p: {ll: v[..., ubic_res] for ll, v in res_calib[p].items()} for p in paráms}
                else:
                    nv, í = ubic_res
                    resultados[lg] = {
                        p: {ll: v[..., í] for ll, v in res_calib['mu_{}_nv_{}'.format(p, nv)].items()}
                        for p in paráms
                    }

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
