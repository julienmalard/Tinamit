from warnings import warn as avisar

import numpy as np
import pymc3 as pm
from scipy.optimize import minimize
import scipy.stats as estad
from scipy.stats import gaussian_kde

from tinamit import _


def calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y, info_gen_aprioris=None, **ops):
    if info_gen_aprioris is not None:
        dists_potenciales = {'Exponencial': estad.expon, 'Gamma': estad.gamma,
                             'Normal': estad.norm, 'T': estad.t, 'Uniforme': estad.uniform}
        dists_pm = {'Exponencial': pm.Normal, 'Gamma': pm.Gamma, 'Laplace': pm.Laplace,
                    'Normal': pm.Normal, 'T': pm.StudentT, 'Uniforme': pm.Uniform}

        aprioris = []
        for d in info_gen_aprioris:
            ajust_sp = ajust_dist(datos=d, dists_potenciales=dists_potenciales)
            dist = dists_pm[ajust_sp['tipo']]
            prms_sp = ajust_sp['prms']
            if dist == 'Exponencial':
                prms = {'lam': 1/prms_sp[1]}
            elif dist == 'Gamma':
                prms = {'alpha': prms_sp[0], 'beta': prms_sp[2]}
            elif dist == 'Normal':
                prms = {'mu': prms_sp[0], 'sd': prms_sp[1]}
            elif dist == 'T':
                prms = {'nu': prms_sp[0], 'mu': prms_sp[1], 'sd': prms_sp[2]}
            elif dist == 'Uniforme':
                prms = {'lower': prms_sp[0], 'upper': prms_sp[0] + prms_sp[1]}
            else:
                raise ValueError
            aprioris.append((dist, prms))
    else:
        aprioris = None

    mod_bayes = obj_ec.gen_mod_bayes(paráms, líms_paráms, obs_x, obs_y, aprioris)
    with mod_bayes:
        t = pm.sample(**ops)

    d_máx = {}
    for p in paráms:
        escl = np.max(t[p])
        if escl < 10e10:
            escl = 1
        try:
            fdp = gaussian_kde(t[p]/escl)
            x = np.linspace(t[p].min()/escl-1, t[p].max()/escl + 1, 1000)
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

        if nombre_dist == 'Exponencial':
            restric = {'floc': 0}
        elif nombre_dist == 'Gamma':
            restric = {'floc': 0}
        elif nombre_dist == 'Normal':
            restric = {}
        elif nombre_dist == 'T':
            restric = {}
        elif nombre_dist == 'Uniforme':
            restric = {}
        else:
            raise ValueError

        try:
            tupla_prms = dist_sp.fit(datos, **restric)
        except:
            tupla_prms = None

        if tupla_prms is not None:
            # Medir el ajuste de la distribución
            p = estad.kstest(rvs=datos, cdf=dist_sp(**tupla_prms).cdf)[1]

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if p > mejor_ajuste['p'] or mejor_ajuste['tipo'] == '':
                # Guardarlo
                mejor_ajuste['p'] = p
                mejor_ajuste['prms'] = tupla_prms
                mejor_ajuste['tipo'] = nombre_dist

    # Si no logramos un buen aujste, avisar al usuario.
    if mejor_ajuste['p'] <= 0.10:
        avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(mejor_ajuste['p'], 4))

    # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
    return mejor_ajuste
