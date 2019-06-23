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

        sub_lugares = {lg: lugar[lg].lugares() for lg in lugares}
        lugs_obs = obs['lugar'].values
        for lg, subs in sub_lugares.items():
            lugs_obs[np.isin(lugs_obs, subs)] = lg
        obs['lugar'] = ('n', lugs_obs)
        obs = obs.where(obs['lugar'].isin(lugares), drop=True)

        # Si hay distribución geográfica, es un poco más complicado.
        if jerárquico:
            # Si estamos implementando un modelo jerárquico...

            # Primero, crear una lista de las relaciones jerárquicas, el cual se necesita para crear el modelo
            # jerárquico bayes.

            def _gen_nv_jerarquía(jrq, egr=None, nv_ant=None):
                """

                Parameters
                ----------
                jrq: dict
                    La jerarquía.
                egr: list
                    Parámetro para la recursión.
                nv_ant: list
                    Un lista de los nombres del nivel superior en la jerarquía. Parámetro de recursión.

                Returns
                -------
                list:
                """

                # Empezar con el primer nivel
                if nv_ant is None:
                    nv_ant = [None]

                # Empezar con egresos vacíos
                if egr is None:
                    egr = []

                nv_act = [x for x in jrq if jrq[x] in nv_ant]

                if len(nv_act):
                    nv_act += [x for x in nv_ant if x in lugares and x not in nv_act]

                    # Agregar a los egresos
                    egr.append(nv_act)

                    # Recursarr en los niveles inferiores
                    _gen_nv_jerarquía(jrq, egr=egr, nv_ant=nv_act)

                # Devolver el resultado
                return egr

            # Generar la lista de relaciones jerárquicas
            nv_jerarquía = _gen_nv_jerarquía(jerarquía)

            nv_jerarquía.insert(0, [None])

            for í, nv in list(enumerate(nv_jerarquía))[::-1]:

                if í == (len(nv_jerarquía) - 1):

                    nv[:] = [x for x in nv if obs['lugar'].isin(x).sum()]
                else:

                    nv[:] = [x for x in nv if x in [jerarquía[y] for y in nv_jerarquía[í + 1]]]

            í_nv_jerarquía = [np.array([nv_jerarquía[í - 1].index(jerarquía[x]) for x in y])
                              for í, y in list(enumerate(nv_jerarquía))[:0:-1]]
            í_nv_jerarquía.insert(0, np.array([nv_jerarquía[-1].index(x) for x in obs['lugar'].values.tolist()]))

            # Generar el modelo bayes
            mod_bayes_jrq = ec.gen_mod_bayes(
                líms_paráms=líms_paráms, obs_x=obs[vars_x], obs_y=obs[var_y],
                aprioris=None, binario=binario, nv_jerarquía=í_nv_jerarquía[::-1],
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
                for p in paráms
            })

            # Calibrar
            res_calib = _calibrar_mod_bayes(
                mod_bayes_jrq, paráms=paráms + prms_extras, ops=ops_método
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
            for lg in lugares:
                lgs_potenciales = lugar.lugares(en=lg)
                obs_lg = obs.where(obs['lugar'].isin(lgs_potenciales + [lg]), drop=True)

                if len(obs_lg['n']):
                    mod_bayes = símismo.ec.gen_mod_bayes(
                        líms_paráms=líms_paráms, obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y],
                        binario=False, aprioris=None, nv_jerarquía=None
                    )
                    resultados[lg] = _calibrar_mod_bayes(
                        mod_bayes=mod_bayes, paráms=símismo.paráms, obs=obs_lg, ops=ops
                    )
                else:
                    resultados[lg] = None

        return {ll: v for ll, v in resultados.items() if ll in lugares}


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
