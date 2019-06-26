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

    def validar(símismo, t, datos, paráms=None, funcs=None):
        vals_datos = datos.obt_vals()

        valids = {}
        for lg in datos.lugares:
            prms_lg = paráms[lg] if lg in paráms else {}
            # if isinstance(t, TiempoCalendario):
            # datos_inic = datos.interpolar('Población', fechas=qij)
            # prms_lg.update(datos_inic)
            datos_lg = vals_datos.where(vals_datos[_('lugar')] == lg, drop=True)
            valids[lg] = ValidadorMod(símismo.mod).validar(t, datos=datos_lg, paráms=prms_lg, funcs=funcs)

        return valids
