from tqdm import tqdm

from tinamit.config import _
from tinamit.mod import OpsSimulGrupo
from .mod import CalibradorModSpotPy
from .valid import ValidadorMod, vars_datos_interés


class SimuladorGeog(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def simular(símismo, t, vals_geog, vals_const=None, vars_interés=None):
        vals_const = vals_const or {}

        ops = OpsSimulGrupo(
            t=t, extern=[dict(**vals_const, **vls_lg) for vls_lg in vals_geog.values()],
            vars_interés=vars_interés, nombre=list(vals_geog)
        )
        return símismo.mod.simular_grupo(ops_grupo=ops)


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

        vars_interés = vars_datos_interés(símismo.mod, datos, corresp_vars=corresp_vars)

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
