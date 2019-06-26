import xarray as xr
from tinamit.datos.bd import BD

from ._utils import eval_funcs


class ValidadorMod(object):
    def __init__(símismo, mod):
        símismo.mod = mod

    def validar(símismo, t, datos, paráms=None, funcs=None):
        if not isinstance(datos, xr.Dataset):
            datos = datos if isinstance(datos, BD) else BD(datos)
            datos = datos.obt_vals()
        funcs = funcs or list(eval_funcs)

        res = símismo.mod.simular(t=t, vals_extern=paráms, vars_interés=datos.data_vars)

        valid = {str(r): _valid_res(r, datos[str(r)].values, funcs) for r in res}
        return valid


def _valid_res(res, obs, funcs):
    vlds = {}
    for f in funcs:
        vlds[f] = eval_funcs[f.lower()](obs, res.vals.values[:, 0])  # para hacer: dimensiones múltiples
    return vlds
