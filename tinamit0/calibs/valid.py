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

    def validar(símismo, t, datos, paráms=None, funcs=None, vars_extern=None, corresp_vars=None, clima=None):
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
        if not isinstance(datos, pd.DataFrame):
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

        vals_extern = datos[list({_resolver_var(v, corresp_vars) for v in vars_extern}) + [_('fecha')]]

        # Para hacer: inter y extrapolación como opción en todas simulaciones, y extrapolación con función según líms
        if not np.datetime64(t.f_inic) in vals_extern[_('fecha')].values:
            vals_extern = vals_extern.append({_('fecha'): pd.to_datetime(t.f_inic)}, ignore_index=True)
        vals_extern = vals_extern.sort_values(_('fecha'))
        vals_extern = vals_extern.interpolate(limit_area='inside').bfill()

        vals_extern = vals_extern.set_index(_('fecha'))
        extern = {vr: vals_extern[_resolver_var(vr, corresp_vars)].dropna() for vr in vars_extern}
        extern = {ll: v for ll, v in extern.items() if len(v)}

        res = símismo.mod.simular()

        vals_calib = datos[list({_resolver_var(v, corresp_vars) for v in vars_valid}) + [_('fecha')]]
        # Para hacer: inter y extrapolación como opción en todas simulaciones, y extrapolación con función según líms
        if not np.datetime64(t.f_inic) in vals_calib[_('fecha')].values:
            vals_calib = vals_calib.append({_('fecha'): pd.to_datetime(t.f_inic)}, ignore_index=True)
        vals_calib = vals_calib.sort_values(_('fecha'))
        vals_calib_interp = vals_calib.interpolate(limit_area='inside').set_index(_('fecha'))
        vals_calib = vals_calib.set_index(_('fecha'))
        vals_calib.loc[t.f_inic] = vals_calib_interp.loc[t.f_inic]

        # Para hacer: si implementamos Dataset en ResultadosSimul este se puede combinar en una línea
        valid = {}
        for r in res:
            vr_datos = _resolver_var(str(r), corresp_vars)
            vals_calib_vr = vals_calib[vr_datos].dropna()
            if len(vals_calib_vr):
                eje = r.vals[_('fecha')].values
                eje_obs = pd.to_datetime(vals_calib_vr.index.values)
                eje_res = relativizar_eje(eje, eje_obs)
                buenas_fechas = np.logical_and(eje_res[0] <= eje_obs, eje_obs <= eje_res[-1])
                datos_r = vals_calib_vr[buenas_fechas]
                if len(datos_r) > 1:
                    fechas_obs = datos_r.index
                    interpoladas = r.interpolar(fechas=fechas_obs)
                    buenas = np.isfinite(r.interpolar(fechas=fechas_obs)).values[:, 0]
                    valid[str(r)] = _valid_res(
                        datos_r.values[buenas], interpoladas.values[buenas], datos_r.index[buenas], funcs
                    )
        return valid


def _valid_res(obs, res, fechas, funcs):
    vlds = {}
    for f in funcs:
        if len(obs) > 1:
            vlds[f] = eval_funcs[f.lower()](obs, res[:, 0], fechas)  # para hacer: dimensiones múltiples
    return vlds


def _resolver_var(var, corresp_vars):
    if var.startswith('"'):
        var = var[1:-1]
    if not corresp_vars or var not in corresp_vars:
        return var
    return corresp_vars[var]


def buscar_vars_interés(mod, datos, corresp_vars):
    variables = datos.columns if isinstance(datos, pd.DataFrame) else datos.variables
    return [v.nombre for v in mod.variables if _resolver_var(v.nombre, corresp_vars) in variables]


def vars_datos_interés(mod, datos, corresp_vars):
    return {_resolver_var(v, corresp_vars) for v in buscar_vars_interés(mod, datos, corresp_vars=corresp_vars)}
