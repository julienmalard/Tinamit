from warnings import warn as avisar

import numpy as np
from scipy.optimize import minimize
from scipy.stats.kde import gaussian_kde

from tinamit import _
from tinamit.EnvolturaMDS.sintaxis import Ecuación
from tinamit.Incertidumbre.Datos import SuperBD
from tinamit.Modelo import Modelo

try:
    import pymc3 as pm
except ImportError:
    pm = None


class ConexDatos(object):
    def __init__(símismo, bd, modelo):
        """

        :param bd:
        :type bd: SuperBD
        :param modelo:
        :type modelo: Modelo
        """

        símismo.bd = bd
        símismo.modelo = modelo
        símismo.dic_info_calib = {}

    def estab_calib_ec(símismo, var, ec=None, paráms=None, método=None, ops_método=None, regional=True):
        símismo.dic_info_calib[var] = {
            'ec': ec,
            'paráms': paráms,
            'método': método,
            'ops_método': ops_método,
            'regional': regional
        }

    def borrar_calib_ec(símismo, var):
        símismo.dic_info_calib.pop(var)

    def calib_ecs(símismo, lugar=None, escala=None, fechas=None, bds=None, nombre='Calib Tinamït'):

        mod = símismo.modelo
        if nombre not in mod.calibs:
            mod.calibs[nombre] = {}

        for var, d_info in símismo.dic_info_calib.items():

            if var not in símismo.modelo.variables:
                avisar(_('El variable "{}" no existe en modelo "{}" y por tanto no se pudo calibrar.')
                       .format(var, símismo.modelo))
                continue

            calibración = símismo.calib_ec(var=var, lugar=lugar, escala=escala, fechas=fechas, bds=bds, **d_info)
            for lg, clb_lg in calibración.items():
                if lg not in mod.calibs[nombre]:
                    mod.calibs[nombre][lg] = {}
                mod.calibs[nombre][lg][var] = clb_lg

    def calib_ec(símismo, var, ec=None, paráms=None, método=None, ops_método=None,
                 lugar=None, escala=None, fechas=None, bds=None):

        símismo.estab_calib_ec(var=var, ec=ec, paráms=paráms, método=método, ops_método=ops_método,
                               regional=escala != 'individual')

        mod = símismo.modelo

        lugares = símismo.bd.geog.obt_lugares_en(lugar, escala=escala)

        if ops_método is None:
            ops_método = {}

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

        obj_ec = Ecuación(ec=ec, dialecto=símismo.modelo.__class__.__name__)
        vars_x = [x for x in obj_ec.variables() if x not in paráms]

        # Buscar los límites teoréticos de los parámetros
        líms_paráms = []
        for p in paráms:
            try:
                rango = mod.variables[p]['rango']
                líms_paráms.append((None if rango[0] is None else rango[0],
                                    None if rango[1] is None else rango[1]))
            except KeyError:
                líms_paráms.append((None, None))

        d_calib = {}
        for cód_lg in lugares:

            obs_y = símismo.bd.obt_datos(l_vars=var, cód_lugar=cód_lg, datos=bds, fechas=fechas)
            obs_x = símismo.bd.obt_datos(l_vars=vars_x, cód_lugar=cód_lg, datos=bds, fechas=fechas)
            if método.lower() == 'Inf Bayes':

                resultados = calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y, **ops_método)

            elif método.lower() == 'Optimizar':
                resultados = optimizar(obj_ec, paráms, líms_paráms, obs_x, obs_y, **ops_método)

            else:
                raise ValueError('')

            d_calib[cód_lg] = resultados

        return d_calib

    def cargar_modelo(símismo, modelo):
        símismo.modelo = modelo
        for var in símismo.dic_info_calib:
            if var not in modelo.variables:
                avisar(_('El variable "{}" no existe en el nuevo modelo.').format(var))

    def no_calibrados(símismo):
        return [var for var in símismo.modelo.variables if var not in símismo.dic_info_calib]


def calib_bayes(obj_ec, paráms, líms_paráms, obs_x, obs_y, **ops):
    mod_bayes = obj_ec.gen_mod_bayes(paráms, líms_paráms, obs_x, obs_y)
    with mod_bayes:
        t = pm.sample(**ops)

    d_máx = {}
    for p in paráms:
        t_p = t[p]
        ys = gaussian_kde(t_p)()
        xs = np.linspace(t_p.min(), t_p.max(), 1000)
        máx = xs[np.argmax(ys)]

        d_máx[p] = máx

    return {p: {'val': d_máx[p], 'dist': t[p]} for p in paráms}


def optimizar(obj_ec, paráms, líms_paráms, obs_x, obs_y, **ops):
    try:
        med_ajuste = ops['med_ajuste']
    except KeyError:
        med_ajuste = 'rmec'

    ec_tx, d_vars = obj_ec.gen_texto()

    def f(p, datos_y):

        d_x = {xv: obs_x[x] for x, xv in d_vars.items()}

        if med_ajuste.lower() == 'rmec':
            def f_ajuste(y, y_o):
                return np.sqrt(np.sum(np.square(y - y_o)) / len(y))
        else:
            raise ValueError('')

        return f_ajuste(eval(ec_tx), datos_y)

    x0 = np.array([np.mean(lp) if None not in lp else 0 for lp in líms_paráms])
    opt = minimize(f, x0=x0, args=obs_y, bounds=líms_paráms, **ops)

    if not opt.success:
        avisar(_('Error de optimización.'))

    return {p: {'val': opt.x[i]} for i, p in enumerate(paráms)}
