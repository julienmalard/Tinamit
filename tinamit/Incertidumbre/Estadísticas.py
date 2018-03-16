from warnings import warn as avisar

import numpy as np
import pymc3 as pm
from scipy.optimize import minimize
import scipy.stats as estad
from scipy.stats import gaussian_kde

from tinamit import _


def calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y, dists_aprioris=None, **ops):

    if dists_aprioris is not None:
        aprioris = []
        for p, dic in dists_aprioris.items():
            pts = dic['dist']
            escl = np.max(pts)
            if escl < 10e10:
                escl = 1
            fdp = gaussian_kde(pts / escl)
            x = np.linspace(pts.min() / escl - 1, pts.max() / escl + 1, np.size(pts))

            pts_fdp = fdp.evaluate(x) * escl

            if p == 'a':
                apriori = (pm.Normal, {'sd': 1, 'mu': 14.5})
            elif p == 'b':
                apriori = (pm.Normal, {'sd': .5, 'mu': 1})
            else:
                apriori = (pm.Gamma, {'alpha': 1, 'beta': 1})
            apriori = (pm.Interpolated, {
                'x_points': x[np.where(pts_fdp!=0)], 'pdf_points': pts_fdp[np.where(pts_fdp!=0)], 'testval': 2
            })
            aprioris.append(apriori)
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
