from warnings import warn as avisar

import numpy as np
import scipy.stats as estad
from scipy.optimize import minimize
from scipy.stats import gaussian_kde

from tinamit import _
from tinamit.Análisis.sintaxis import Ecuación

try:
    import pymc3 as pm
except ImportError:
    pm = None

if pm is None:
    dists = None
else:
    dists = {'Beta': {'sp': estad.beta, 'pm': pm.Beta,
                      'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[1]},
                      'líms': (0, 1)},
             'Cauchy': {'sp': estad.cauchy, 'pm': pm.Cauchy,
                        'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[1]},
                        'líms': (None, None)},
             'Chi2': {'sp': estad.chi2, 'pm': pm.ChiSquared,
                      'sp_a_pm': lambda p: {'df': p[0]},
                      'líms': (0, None)},
             'Exponencial': {'sp': estad.expon, 'pm': pm.Exponential,
                             'sp_a_pm': lambda p: {'lam': 1 / p[1]},
                             'líms': (0, None)},
             'Gamma': {'sp': estad.gamma, 'pm': pm.Gamma,
                       'sp_a_pm': lambda p: {'alpha': p[0], 'beta': 1 / p[2]},
                       'líms': (0, None)},
             'Laplace': {'sp': estad.laplace, 'pm': pm.Laplace,
                         'sp_a_pm': lambda p: {'mu': p[0], 'b': p[1]},
                         'líms': (None, None)},
             'LogNormal': {'sp': estad.lognorm, 'pm': pm.Lognormal,
                           'sp_a_pm': lambda p: {'mu': p[1], 'sd': p[2]},
                           'líms': (0, None)},
             'MitadCauchy': {'sp': estad.halfcauchy, 'pm': pm.HalfCauchy,
                             'sp_a_pm': lambda p: {'beta': p[1]},
                             'líms': (0, None)},
             'MitadNormal': {'sp': estad.halfnorm, 'pm': pm.HalfNormal,
                             'sp_a_pm': lambda p: {'sd': p[1]},
                             'líms': (0, None)},
             'Normal': {'sp': estad.norm, 'pm': pm.Normal,
                        'sp_a_pm': lambda p: {'mu': p[0], 'sd': p[1]},
                        'líms': (None, None)},
             'T': {'sp': estad.t, 'pm': pm.StudentT,
                   'sp_a_pm': lambda p: {'nu': p[0], 'mu': p[1], 'sd': p[2]},
                   'líms': (None, None)},
             'Uniforme': {'sp': estad.uniform, 'pm': pm.Uniform,
                          'sp_a_pm': lambda p: {'lower': p[0], 'upper': p[0] + p[1]},
                          'líms': (0, 1)},
             'Weibull': {'sp': estad.weibull_min, 'pm': pm.Weibull,
                         'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[2]},
                         'líms': (0, None)},
             }


class Calibrador(object):
    def __init__(símismo, ec, otras_ecs=None, nombres_equiv=None):

        símismo.ec = Ecuación(ec, otras_ecs=otras_ecs, nombres_equiv=nombres_equiv)

    def calibrar(símismo, bd_datos, paráms=None, líms_paráms=None, método=None, binario=False, en=None,
                 escala=None, ops_método=None):

        if ops_método is None:
            ops_método = {}

        vars_ec = símismo.ec.variables()
        var_y = símismo.ec.nombre
        if var_y not in bd_datos.vars:
            raise ValueError(_('El variable "{}" no parece existir en la base de datos.').format(var_y))

        if paráms is None:
            paráms = [x for x in vars_ec if x not in bd_datos.vars]
        vars_x = [v for v in vars_ec if v not in paráms]

        if líms_paráms is None:
            líms_paráms = {}

        líms_paráms_final = {}
        for p in paráms:
            if p not in líms_paráms:
                líms_paráms_final[p] = (None, None)
            elif líms_paráms[p] is None:
                líms_paráms_final[p] = (None, None)
            else:
                if len(líms_paráms[p]) == 2:
                    líms_paráms_final[p] = líms_paráms[p]
                else:
                    raise ValueError(_('Los límites de parámetros deben tener dos elementos: (mínimo, máximo). Utilizar'
                                       '``None`` para ± infinidad: (None, 10); (0, None).'))

        if método is None:
            if pm is not None:
                método = 'inferencia bayesiana'
            else:
                método = 'optimizar'
        else:
            método = método.lower()

        try:
            lugares = bd_datos.geog_obt_lugares_en(en, escala=escala)
            jerarquía = bd_datos.geog_obt_jerarquía(en, escala=escala)
        except ValueError:
            lugares = jerarquía = None

        if método == 'inferencia bayesiana':
            return símismo._calibrar_bayesiana(
                var_y=var_y, vars_x=vars_x, líms_paráms=líms_paráms_final, binario=binario,
                ops_método=ops_método, bd_datos=bd_datos, lugares=lugares, jerarquía=jerarquía
            )
        elif método == 'optimizar':
            return símismo._calibrar_optim(
                paráms=paráms, var_y=var_y, vars_x=vars_x, líms_paráms=líms_paráms_final,
                ops_método=ops_método, bd_datos=bd_datos, lugares=lugares, jerarquía=jerarquía
            )
        else:
            raise ValueError(_('Método de calibración "{}" no reconocido.').format(método))

    def _calibrar_bayesiana(símismo, var_y, vars_x, líms_paráms, binario, ops_método,
                            bd_datos, lugares, jerarquía, mod_jerárquico=False):

        if pm is None:
            raise ImportError(_('Debes instalar PyMC3 para poder hacer calibraciones con inferencia bayesiana.'))

        l_vars = vars_x + [var_y]
        obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True)

        if lugares is None:
            resultados = _calibrar_mod_bayes(
                ec=símismo.ec, líms_paráms=líms_paráms, obs=obs, vars_x=vars_x, var_y=var_y,
                binario=binario, aprioris=None, ops=ops_método
            )

        else:
            if mod_jerárquico:
                raise NotImplementedError
            else:
                def _calibrar_jerárquíco_manual(lugar, jrq, clbs=None):
                    if clbs is None:
                        clbs = {}

                    if lugar is None:
                        obs_lg = obs
                        aprs = pariente = None
                    else:
                        lgs_potenciales = bd_datos.geog.obt_lugares_en(lugar)
                        obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lugar])]
                        try:
                            pariente = jrq[lugar]
                            if pariente not in clbs:
                                _calibrar_jerárquíco_manual(lugar=pariente, jrq=jrq, clbs=clbs)
                            aprs = _gen_a_prioris(líms=líms_paráms, dic_clbs=clbs[pariente])
                        except KeyError:
                            raise ValueError(
                                _('El lugar "{}" no está bien inscrito en la jerarquía general.')
                                   .format(lugar)
                            )

                    if len(obs_lg):
                        clbs[lugar] = _calibrar_mod_bayes(
                            ec=símismo.ec, líms_paráms=líms_paráms, obs=obs_lg, vars_x=vars_x, var_y=var_y,
                            binario=binario, aprioris=aprs, ops=ops_método
                        )
                    else:
                        clbs[lugar] = clbs[pariente]

                resultados = {}
                for lg in lugares:
                    _calibrar_jerárquíco_manual(lugar=lg, jrq=jerarquía, clbs=resultados)

        return resultados

    def _calibrar_optim(símismo, paráms, var_y, vars_x, líms_paráms, ops_método, bd_datos, lugares, jerarquía):
        """

        Parameters
        ----------
        paráms :
        var_y :
        vars_x :
        líms_paráms :
        ops_método :
        bd_datos : SuperBD
        lugares :
        jerarquía :

        Returns
        -------

        """
        f_python = símismo.ec.gen_func_python(paráms=paráms)

        l_vars = vars_x + [var_y]

        if lugares is None:
            obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True)
            resultados = _optimizar(f_python, paráms=paráms, líms_paráms=líms_paráms,
                                    obs_x=obs[vars_x], obs_y=obs[var_y], **ops_método)
        else:
            obs = bd_datos.obt_datos(l_vars=l_vars, excl_faltan=True)

            def _calibrar_jerárchico_manual(lugar, jrq, clbs=None):
                if clbs is None:
                    clbs = {}

                if lugar is None:
                    obs_lg = obs
                else:
                    lgs_potenciales = bd_datos.geog.obt_lugares_en(lugar)
                    obs_lg = obs[obs['lugar'].isin(lgs_potenciales + [lugar])]
                if len(obs_lg):
                    resultados[lugar] = _optimizar(
                        f_python, paráms=paráms, líms_paráms=líms_paráms,
                        obs_x=obs_lg[vars_x], obs_y=obs_lg[var_y], **ops_método
                    )
                else:
                    try:
                        pariente = jrq[lugar]
                        if pariente not in clbs:
                            _calibrar_jerárchico_manual(lugar=pariente, jrq=jrq, clbs=clbs)
                        resultados[lugar] = clbs[pariente]

                    except KeyError:
                        avisar(_('No encontramos datos para el lugar "{}", ni siguiera en su jerarquía, y por eso'
                                 'no pudimos calibrarlo.').format(lugar))
                        resultados[lugar] = {}

            resultados = {}
            for lg in lugares:
                _calibrar_jerárchico_manual(lugar=lg, jrq=jerarquía, clbs=resultados)
        if lugares is not None:
            return {ll: v for ll, v in resultados.items() if ll in lugares}
        else:
            return resultados


def _gen_a_prioris(líms, dic_clbs):
    aprioris = {}
    for p, dic in dic_clbs.items():
        lp = líms[p]

        ajust_sp = _ajust_dist(datos=dic['dist'], líms=lp)
        nombre = ajust_sp['tipo']
        dist_pm = dists[nombre]['pm']

        prms_sp = ajust_sp['prms']
        prms_pm = dists[nombre]['sp_a_pm'](prms_sp)

        aprioris[p] = (dist_pm, prms_pm)

    return aprioris


def _calibrar_mod_bayes(ec, líms_paráms, obs, vars_x, var_y, binario, aprioris, ops):
    mod_bayes = ec.gen_mod_bayes(
        líms_paráms=líms_paráms,
        obs_x=obs[vars_x], obs_y=obs[var_y],
        aprioris=aprioris, binario=binario
    )
    with mod_bayes:
        ops_auto = {
            'tune': 1000,
            'cores': 1
        }
        ops_auto.update(ops)
        t = pm.sample(**ops_auto)

    return _procesar_calib_bayes(t, paráms=list(líms_paráms))


def _procesar_calib_bayes(traza, paráms):
    d_máx = {}
    for p in paráms:
        escl = np.max(traza[p])
        rango = escl - np.min(traza[p])
        if escl < 10e10:
            escl = 1
        try:
            fdp = gaussian_kde(traza[p] / escl)
            x = np.linspace(traza[p].min() / escl - 1 * rango, traza[p].max() / escl + 1 * rango, 1000)
            máx = x[np.argmax(fdp.evaluate(x))] * escl
            d_máx[p] = máx
        except BaseException:
            d_máx[p] = None

    return {p: {'val': d_máx[p], 'dist': traza[p]} for p in paráms}


def _optimizar(func, paráms, líms_paráms, obs_x, obs_y, **ops):
    try:
        med_ajuste = ops['med_ajuste']
    except KeyError:
        med_ajuste = 'rmec'

    def f(prm):

        if med_ajuste.lower() == 'rmec':
            def f_ajuste(y, y_o):
                return np.sqrt(np.sum(np.square(y - y_o)) / len(y))
        else:
            raise ValueError('')

        return f_ajuste(func(prm, obs_x), obs_y)

    x0 = []
    for p in paráms:
        lp = líms_paráms[p]
        if lp[0] is None:
            if lp[1] is None:
                x0.append(0)
            else:
                x0.append(lp[1])
        else:
            if lp[1] is None:
                x0.append(lp[0])
            else:
                x0.append((lp[0] + lp[1]) / 2)

    x0 = np.array(x0)
    opt = minimize(f, x0=x0, bounds=[líms_paráms[p] for p in paráms], **ops)

    if not opt.success:
        avisar(_('Error de optimización para ecuación "{}".').format(str(func)))

    return {p: {'val': opt.x[i]} for i, p in enumerate(paráms)}


def _ajust_dist(datos, líms):
    mejor_ajuste = {'p': 0, 'tipo': None}

    dists_potenciales = {ll: v['sp'] for ll, v in dists.items() if _líms_compat(líms, v['líms'])}

    for nombre_dist, dist_sp in dists_potenciales.items():

        if nombre_dist == 'Beta':
            restric = {'floc': líms[0], 'fscale': líms[1] - líms[0]}
        elif nombre_dist == 'Cauchy':
            restric = {}
        elif nombre_dist == 'Chi2':
            restric = {'floc': líms[0], 'fscale': líms[1] - líms[0]}
        elif nombre_dist == 'Exponencial':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'Gamma':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'Laplace':
            restric = {}
        elif nombre_dist == 'LogNormal':
            restric = {'fs': 1}
        elif nombre_dist == 'MitadCauchy':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'MitadNormal':
            restric = {'floc': líms[0]}
        elif nombre_dist == 'Normal':
            restric = {}
        elif nombre_dist == 'T':
            restric = {}
        elif nombre_dist == 'Uniforme':
            restric = {}
        elif nombre_dist == 'Weibull':
            restric = {'floc': líms[0]}
        else:
            raise ValueError

        try:
            tupla_prms = dist_sp.fit(datos, **restric)
        except:
            tupla_prms = None

        if tupla_prms is not None:
            # Medir el ajuste de la distribución
            p = estad.kstest(rvs=datos, cdf=dist_sp(*tupla_prms).cdf)[1]

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if p > mejor_ajuste['p'] or mejor_ajuste['tipo'] is None:
                # Guardarlo
                mejor_ajuste['p'] = p
                mejor_ajuste['prms'] = tupla_prms
                mejor_ajuste['tipo'] = nombre_dist

    # Si no logramos un buen aujste, avisar al usuario.
    if mejor_ajuste['p'] <= 0.10:
        avisar('El ajuste de la mejor distribución quedó muy mal (p = {}).'.format(round(mejor_ajuste['p'], 4)))

    # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
    return mejor_ajuste


def _líms_compat(l_1, l_2):
    l_1 = [None if x is None or np.isinf(x) else 0 for x in l_1]
    l_2 = [None if x is None or np.isinf(x) else 0 for x in l_2]

    return l_1 == l_2
