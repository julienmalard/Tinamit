import numpy as np
import xarray as xr

from tinamit.config import _
from tinamit.datos.bd import BD, interpolar_xr
from tinamit.mod import EspecTiempo
from ._utils import eval_funcs


class ValidadorMod(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def validar(símismo, t, datos, paráms=None, funcs=None, vars_extern=None, corresp_vars=None):

        t = t if isinstance(t, EspecTiempo) else EspecTiempo(t)
        if not isinstance(datos, xr.Dataset):
            datos = datos if isinstance(datos, BD) else BD(datos)
            datos = datos.obt_vals(
                [x for x in datos.variables if _reversar_var(x, corresp_vars) in símismo.mod.variables]
            )

        funcs = funcs or list(eval_funcs)
        vars_extern = vars_extern or []
        if not isinstance(vars_extern, list):
            vars_extern = [vars_extern]

        vars_interés = [x for x in datos.data_vars if _reversar_var(x, corresp_vars) in símismo.mod.variables]
        vars_extern = [x for x in vars_interés if _reversar_var(x, corresp_vars) in vars_extern]
        vars_valid = [x for x in vars_interés if x not in vars_extern]

        vals_extern = datos[vars_extern]
        extern = {vr: vals_extern[vr] for vr in vars_extern}

        if t.f_inic is not None:

            datos_inic = interpolar_xr(datos, t.f_inic)
            if datos_inic.sizes['n']:
                for vr in vars_interés:
                    if vr not in extern:
                        extern[vr] = datos_inic[vr].values

        res = símismo.mod.simular(t=t, extern={**paráms, **extern}, vars_interés=vars_valid)

        vals_calib = datos[vars_valid]
        # Para hacer: si implementamos Dataset en ResultadosSimul este se puede combinar en una línea
        valid = {}
        for r in res:
            eje = r.vals[_('fecha')].values
            buenas_fechas = np.logical_and(eje[0] <= vals_calib[_('fecha')], vals_calib[_('fecha')] <= eje[-1])
            datos_r = vals_calib[str(r)].where(buenas_fechas, drop=True).dropna('n')
            if datos_r.sizes['n']:
                fechas_obs = datos_r[_('fecha')]
                interpoladas = r.interpolar(fechas=fechas_obs)
                valid[str(r)] = _valid_res(datos_r.values, interpoladas.values, funcs)
        return valid


def _valid_res(obs, res, funcs):
    vlds = {}
    for f in funcs:
        vlds[f] = eval_funcs[f.lower()](obs, res[:, 0])  # para hacer: dimensiones múltiples
    return vlds


# Para hacer: duplicado de simul.py
def _reversar_var(var, corresp_vars):
    if not corresp_vars:
        return var
    return next((ll for ll, v in corresp_vars.items() if v == var), var)
