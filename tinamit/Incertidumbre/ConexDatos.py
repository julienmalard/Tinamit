import pymc3 as pm
import numpy as np
from scipy.stats.kde import gaussian_kde
from scipy.optimize import minimize

from tinamit.EnvolturaMDS.sintaxis import Ecuación


class ConexDatos(object):
    def __init__(símismo, bd, modelo):
        símismo.bd = bd
        símismo.modelo = modelo

    def calib_ec(símismo, var, ec=None, paráms=None, método=None):

        mod = símismo.modelo

        d_var = mod.variables[var]

        if paráms is None:
            paráms = [x for x in d_var['parientes'] if x in mod.constantes]
        if not isinstance(paráms, list):
            paráms = [paráms]

        if ec is None:
            ec = d_var['ec']

        if método is None:
            if pm:
                método = 'Inf Bayes'
            else:
                método = 'Optimizar'

        obj_ec = Ecuación(ec=ec, dialecto='Vensim')
        if método.lower() == 'Inf Bayes':
            líms_paráms = []
            for p in paráms:
                try:
                    rango = mod.variables[p]['rango']
                    líms_paráms.append((-np.inf if rango[0] is None else rango[0],
                                        np.inf if rango[1] is None else rango[1]))
                except KeyError:
                    líms_paráms.append((-np.inf, np.inf))

            resultados = calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y)

        elif método.lower() == 'Optimizar':
            resultados = optimizar(obj_ec)

        else:
            raise ValueError('')

        dic_info_calib = {}  # para hacer
        dic_info_calib[var] = {'paráms': paráms, 'método': método,
                               'val': resultados['val'], 'dist': resultados['dist']}


def calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y):

    mod_bayes = obj_ec.gen_mod_bayes(paráms, líms_paráms, obs_x, obs_y)
    with mod_bayes:
        t = pm.sample()

    d_máx = {}
    for p in paráms:
        t_p = t[p]
        ys = gaussian_kde(t_p)()
        xs = np.linspace(t_p.min(), t_p.max(), 1000)
        máx = xs[np.argmax(ys)]

        d_máx[p] = máx

    return {p: {'val': d_máx[p], 'dist': t[p]} for p in paráms}


def optimizar(ec, d_vars, med_ajuste):

    ec_tx, d_vars = ec

    def f(p, datos_y, datos_x):

        d_x = {xv: datos_x[x] for x, xv in d_vars.items()}

        if med_ajuste.lower() == 'rmec':
            def f_ajuste(y, y_o):
                return np.sqrt(np.sum(np.square(y - y_o)) / len(y))

        else:
            raise ValueError('')

        return f_ajuste(eval(ec_tx), datos_y)

    opt = minimize(f, )

    return
