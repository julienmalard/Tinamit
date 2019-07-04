from tqdm import tqdm

from tinamit.calibs.mod import CalibradorModSpotPy
from tinamit.calibs.valid import ValidadorMod
from tinamit.config import _


class SimuladorGeog(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def simular(símismo, t, vals_geog, vals_const=None, vars_interés=None):
        vals_const = vals_const or {}

        res = {
            lg: símismo.mod.simular(
                t=t, extern=dict(**vals_const, **vls_lg), vars_interés=vars_interés
            ) for lg, vls_lg in vals_geog.items()
        }
        return res


class CalibradorGeog(object):
    def __init__(símismo, mod, calibrador=CalibradorModSpotPy):
        símismo.mod = mod
        símismo.calibrador = calibrador

    def calibrar(símismo, t, datos, líms_paráms, método='epm', n_iter=300, vars_obs=None, vals_geog=None,
                 vals_const=None):
        vals_datos = datos.obt_vals()
        clbrd = símismo.calibrador(símismo.mod)

        calibs = {}
        for lg in datos.lugares:
            datos_lg = vals_datos.where(vals_datos[_('lugar')] == lg, drop=True)
            calibs[lg] = clbrd.calibrar(líms_paráms, datos=datos_lg, método=método, n_iter=n_iter, vars_obs=vars_obs)

        return calibs


class ValidadorGeog(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def validar(símismo, t, datos, paráms=None, funcs=None, vars_extern=None, corresp_vars=None):

        vars_interés = [x for x in datos.variables if _reversar_var(x, corresp_vars) in símismo.mod.variables]

        vals_datos = datos.obt_vals(vars_interés)

        valids = {}
        for lg in tqdm(datos.lugares):
            prms_lg = paráms[lg] if lg in paráms else {}
            datos_lg = vals_datos.where(vals_datos[_('lugar')] == lg, drop=True)

            if datos_lg.sizes['n']:
                valids[lg] = ValidadorMod(símismo.mod).validar(
                    t, datos=datos_lg, paráms=prms_lg, funcs=funcs, vars_extern=vars_extern, corresp_vars=corresp_vars
                )

        return valids


def _resolver_var(var, corresp_vars):
    if not corresp_vars or var not in corresp_vars:
        return var
    return corresp_vars[var]


def _reversar_var(var, corresp_vars):
    if not corresp_vars:
        return var
    return next((ll for ll, v in corresp_vars.items() if v == var), var)
