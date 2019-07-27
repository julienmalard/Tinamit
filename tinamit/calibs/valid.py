import numpy as np
import pandas as pd
import xarray as xr
from tinamit.config import _
from tinamit.datos.bd import BD
from tinamit.mod.extern import relativizar_eje
from tinamit.tiempo.tiempo import EspecTiempo

from ._utils import eval_funcs


class ValidadorMod(object):
    """
    Clase para efectuar validaciones de un modelo.
    """
    def __init__(símismo, mod):
        """

        Parameters
        ----------
        mod: Modelo
            El modelo para validar.
        """
        símismo.mod = mod

    def validar(símismo, t, datos, paráms=None, funcs=None, vars_extern=None, corresp_vars=None):
        """
        Efectua la validación.

        Parameters
        ----------
        t: int or EspecTiempo
            La especificación de tiempo para la validación.
        datos: xr.Dataset or xr.DataArray or str or pd.DataFrame or dict or Fuente or list
            La base de datos para la validación.
        paráms: dict
            Diccionario de los parámetros calibrados para cada lugar.
        funcs: list
            Funciones de validación para aplicar a los resultados.
        vars_extern: str or list or Variable
            Variable(s) exógenos cuyos valores se tomarán de la base de datos para alimentar la simulación y con
            los cuales por supuesto no se validará el modelo.
        corresp_vars:
            Diccionario de correspondencia entre nombres de valores en el modelo y en la base de datos.

        Returns
        -------
        dict
            Validación por variable.

        """

        t = t if isinstance(t, EspecTiempo) else EspecTiempo(t)
        if not isinstance(datos, xr.Dataset):
            datos = datos if isinstance(datos, BD) else BD(datos)
            datos = datos.obt_vals(
                buscar_vars_interés(símismo.mod, datos, corresp_vars)
            )

        funcs = funcs or list(eval_funcs)
        vars_extern = vars_extern or []
        if not isinstance(vars_extern, list):
            vars_extern = [vars_extern]

        vars_interés = buscar_vars_interés(símismo.mod, datos, corresp_vars)
        vars_valid = [v for v in vars_interés if v not in vars_extern]

        vals_extern = datos[list({_resolver_var(v, corresp_vars) for v in vars_extern})]
        extern = {vr: vals_extern[_resolver_var(vr, corresp_vars)].dropna('n') for vr in vars_extern}
        extern = {ll: v for ll, v in extern.items() if v.sizes['n']}

        res = símismo.mod.simular(t=t, extern={**paráms, **extern}, vars_interés=vars_valid)

        vals_calib = datos[list({_resolver_var(v, corresp_vars) for v in vars_valid})]
        # Para hacer: si implementamos Dataset en ResultadosSimul este se puede combinar en una línea
        valid = {}
        for r in res:
            vr_datos = _resolver_var(str(r), corresp_vars)
            vals_calib_vr = vals_calib[vr_datos].dropna('n')
            if vals_calib_vr.sizes['n']:
                eje = r.vals[_('fecha')].values
                eje_obs = pd.to_datetime(vals_calib_vr[_('fecha')].values)
                eje_res = relativizar_eje(eje, eje_obs)
                buenas_fechas = xr.DataArray(np.logical_and(eje_res[0] <= eje_obs, eje_obs <= eje_res[-1]), dims='n')
                datos_r = vals_calib[vr_datos].where(buenas_fechas, drop=True).dropna('n')
                if datos_r.sizes['n'] > 1:
                    fechas_obs = datos_r[_('fecha')]
                    interpoladas = r.interpolar(fechas=fechas_obs)
                    valid[str(r)] = _valid_res(
                        datos_r.values, interpoladas.values, pd.to_datetime(datos_r[_('fecha')].values), funcs
                    )
        return valid


def _valid_res(obs, res, fechas, funcs):
    vlds = {}
    for f in funcs:
        vlds[f] = eval_funcs[f.lower()](obs, res[:, 0], fechas)  # para hacer: dimensiones múltiples
    return vlds


def _resolver_var(var, corresp_vars):
    if not corresp_vars or var not in corresp_vars:
        return var
    return corresp_vars[var]


def buscar_vars_interés(mod, datos, corresp_vars):
    return [v.nombre for v in mod.variables if _resolver_var(v.nombre, corresp_vars) in datos.variables]


def vars_datos_interés(mod, datos, corresp_vars):
    return {_resolver_var(v, corresp_vars) for v in buscar_vars_interés(mod, datos, corresp_vars=corresp_vars)}
