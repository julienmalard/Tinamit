from tinamit.calibs.mod import CalibradorModSpotPy
from tinamit.calibs.valid import ValidadorMod


class SimuladorGeog(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def simular(símismo, t, vals_geog, vals_const=None, vars_interés=None):
        vals_const = vals_const or {}
        res = {
            lg: símismo.mod.simular(
                t=t, vals_extern=dict(**vals_const, **vls_lg), vars_interés=vars_interés
            ) for lg, vls_lg in vals_geog.items()
        }
        return res


class CalibradorGeog(object):
    def __init__(símismo, mod, calibrador=CalibradorModSpotPy):
        símismo.mod = mod
        símismo.calibrador = calibrador

    def calibrar(símismo, t, datos, líms_paráms, método='epm', n_iter=300, vars_obs=None, vals_geog=None,
                 vals_const=None):
        calibs = {}
        for lg, datos_lg in datos.items():
            clbrd = símismo.calibrador(símismo.mod)
            calibs[lg] = clbrd.calibrar(líms_paráms, datos=datos_lg, método=método, n_iter=n_iter, vars_obs=vars_obs)

        return calibs


class ValidadorGeog(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def validar(símismo, t, datos, paráms, funcs=None):
        valids = {}
        for lg, datos_lg in datos.items():
            valids[lg] = ValidadorMod(símismo.mod).validar(t, datos=datos_lg, paráms=paráms[lg], funcs=funcs)

        return valids
