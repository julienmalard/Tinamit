from warnings import warn as avisar

import numpy as np
try:
    import pymc3 as pm
except ImportError:
    pm = None
from scipy.optimize import minimize
import scipy.stats as estad
from scipy.stats import gaussian_kde

from tinamit import _

if pm is not None:
    dists = {'Beta': {'sp': estad.beta, 'pm': pm.Beta,
                      'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[1]}},
             'Cauchy': {'sp': estad.cauchy, 'pm': pm.Cauchy,
                        'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[1]}},
             'Chi2': {'sp': estad.chi2, 'pm': pm.ChiSquared,
                      'sp_a_pm': lambda p: {'df': p[0]}},
             'Exponencial': {'sp': estad.expon, 'pm': pm.Exponential,
                             'sp_a_pm': lambda p: {'lam': 1/p[1]}},
             'Gamma': {'sp': estad.gamma, 'pm': pm.Gamma,
                       'sp_a_pm': lambda p: {'alpha': p[0], 'beta': 1/p[2]}},
             'Laplace': {'sp': estad.laplace, 'pm': pm.Laplace,
                         'sp_a_pm': lambda p: {'mu': p[0], 'b': p[1]}},
             'LogNormal': {'sp': estad.lognorm, 'pm': pm.Lognormal,
                           'sp_a_pm': lambda p: {'mu': p[1], 'sd': p[2]}},
             'MitadCauchy': {'sp': estad.halfcauchy, 'pm': pm.HalfCauchy,
                             'sp_a_pm': lambda p: {'beta': p[1]}},
             'MitadNormal': {'sp': estad.halfnorm, 'pm': pm.HalfNormal,
                             'sp_a_pm': lambda p: {'sd': p[1]}},
             'Normal': {'sp': estad.norm, 'pm': pm.Normal,
                        'sp_a_pm': lambda p: {'mu': p[0], 'sd': p[1]}},
             'T': {'sp': estad.t, 'pm': pm.StudentT,
                   'sp_a_pm': lambda p: {'nu': p[0], 'mu': p[1], 'sd': p[2]}},
             'Uniforme': {'sp': estad.uniform, 'pm': pm.Uniform,
                          'sp_a_pm': lambda p: {'lower': p[0], 'upper': p[0] + p[1]}},
             'Weibull': {'sp': estad.weibull_min, 'pm': pm.Weibull,
                         'sp_a_pm': lambda p: {'alpha': p[0], 'beta': p[2]}},
             }


def calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y, dists_aprioris=None, binario=False, **ops):
    if pm is None:
        raise ImportError('')
    if dists_aprioris is not None:

        aprioris = []
        for p, dic in dists_aprioris.items():
            ajust_sp = ajust_dist(datos=dic['dist'], dists_potenciales={ll: v['sp'] for ll, v in dists.items()})
            nombre = ajust_sp['tipo']
            dist_pm = dists[nombre]['pm']

            prms_sp = ajust_sp['prms']
            prms_pm = dists[nombre]['sp_a_pm'](prms_sp)

            aprioris.append((dist_pm, prms_pm))
    else:
        aprioris = None

    mod_bayes = obj_ec.gen_mod_bayes(paráms, líms_paráms, obs_x, obs_y, aprioris, binario=binario)
    with mod_bayes:
        ops_auto = {
            'tune': 1000,
        }
        ops_auto.update(ops)
        t = pm.sample(**ops_auto)

    d_máx = {}
    for p in paráms:
        escl = np.max(t[p])
        rango = escl - np.min(t[p])
        if escl < 10e10:
            escl = 1
        try:
            fdp = gaussian_kde(t[p]/escl)
            x = np.linspace(t[p].min()/escl-1*rango, t[p].max()/escl + 1*rango, 1000)
            máx = x[np.argmax(fdp.evaluate(x))] * escl
            d_máx[p] = máx
        except:
            d_máx[p] = None

    return {p: {'val': d_máx[p], 'dist': t[p]} for p in paráms}


def optimizar(obj_ec, paráms, líms_paráms, obs_x, obs_y, **ops):
    try:
        med_ajuste = ops['med_ajuste']
    except KeyError:
        med_ajuste = 'rmec'

    ec = obj_ec.gen_func_python()

    def f(p):

        if med_ajuste.lower() == 'rmec':
            def f_ajuste(y, y_o):
                return np.sqrt(np.sum(np.square(y - y_o)) / len(y))
        else:
            raise ValueError('')

        return f_ajuste(ec(p, obs_x), obs_y)

    x0 = []
    for lp in líms_paráms:
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
    opt = minimize(f, x0=x0, bounds=líms_paráms, **ops)

    if not opt.success:
        avisar(_('Error de optimización par aecuación "{}".').format(str(ec)))

    return {p: {'val': opt.x[i]} for i, p in enumerate(paráms)}


def regresión(obj_ec, paráms, líms_paráms, obs_x, obs_y, **ops):
    raise NotImplementedError

def ajust_dist(datos, dists_potenciales):
    mejor_ajuste = {'p':0, 'tipo':None}

    for nombre_dist, dist_sp in dists_potenciales.items():

        if nombre_dist == 'Beta':
            restric = {'floc': 0, 'fscale': 1}
        elif nombre_dist == 'Cauchy':
            restric = {}
        elif nombre_dist == 'Chi2':
            restric = {'floc': 0, 'fscale': 1}
        elif nombre_dist == 'Exponencial':
            restric = {'floc': 0}
        elif nombre_dist == 'Gamma':
            restric = {'floc': 0}
        elif nombre_dist == 'Laplace':
            restric = {}
        elif nombre_dist == 'LogNormal':
            restric = {'fs': 1}
        elif nombre_dist == 'MitadCauchy':
            restric = {'floc': 0}
        elif nombre_dist == 'MitadNormal':
            restric = {'floc': 0}
        elif nombre_dist == 'Normal':
            restric = {}
        elif nombre_dist == 'T':
            restric = {}
        elif nombre_dist == 'Uniforme':
            restric = {}
        elif nombre_dist == 'Weibull':
            restric = {'floc': 0}
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