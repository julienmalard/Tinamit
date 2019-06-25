import os
from itertools import product

import numpy as np
import pandas as pd
import xarray as xr
from tinamit.config import _

from .fuente import FuentePandas, FuenteDic, FuenteVarXarray, FuenteBaseXarray, FuenteCSV


class BD(object):
    def __init__(símismo, fuentes):
        fuentes = [fuentes] if not isinstance(fuentes, (list, tuple)) else fuentes
        símismo.fuentes = [_gen_fuente(f) for f in fuentes]
        símismo.variables = list(set((v for f in símismo.fuentes for v in f.variables)))

    def obt_vals(símismo, vars_interés=None, lugares=None, fechas=None):
        """

        Parameters
        ----------
        vars_interés
        lugares
        fechas

        Returns
        -------
        xr.DataArray, xr.Dataset
        """
        vr_único = False
        if isinstance(vars_interés, str):
            vars_interés = [vars_interés]
            vr_único = True

        l_vals_fnts = [f.obt_vals(vars_interés=vars_interés, lugares=lugares, fechas=fechas) for f in símismo.fuentes]
        v_lugares = np.unique(np.concatenate([v[_('lugar')].dropna('n') for v in l_vals_fnts]+[['']]))
        v_fechas = np.unique(np.concatenate([v[_('fecha')].dropna('n') for v in l_vals_fnts]+[[np.datetime64('NaT')]]))
        v_lugares.sort()
        v_fechas.sort()

        vals = xr.Dataset(
            data_vars={
                vr: ((_('lugar'), _('fecha')), np.full((v_lugares.size, v_fechas.size), np.nan)) for vr in vars_interés
            },
            coords={_('lugar'): v_lugares, _('fecha'): v_fechas}
        )
        for lg, fch in product(v_lugares, v_fechas):
            fnts_lg_fch = [
                v.where(np.logical_and(
                    np.isnat(v['fecha']) if np.isnat(fch) else v['fecha'] == fch,
                    v['lugar'] == lg), drop=True) for v in l_vals_fnts
                if len(v.data_vars)
            ]
            bd_lg_fch = xr.auto_combine(fnts_lg_fch)
            if not bd_lg_fch.sizes['n']:
                continue
            for vr in vars_interés:
                try:
                    vl = bd_lg_fch[vr].values[0]
                except KeyError:
                    vl = None
                if vl is not None and vl != np.nan:
                    índs = {}
                    if not np.isnat(fch):
                        índs[_('fecha')] = fch
                    if lg:
                        índs[_('lugar')] = lg
                    vals[vr].loc[índs] = vl

        vals = vals.stack(n=[_('fecha'), _('lugar')])
        vals = vals.dropna('n', how='all')

        return vals[vars_interés[0]] if vr_único else vals

    def interpolar(símismo, vars_interés, fechas, lugares=None, extrap=False):
        datos = símismo.obt_vals(vars_interés=vars_interés, lugares=lugares, fechas=None)

        # Las nuevas fechas de interés que hay que a la base de datos
        if not isinstance(fechas, (tuple, list)):
            fechas = [fechas]
        nuevas_fechas = [x for x in pd.DatetimeIndex(fechas) if not (datos[_('fecha')] == x.to_datetime64()).any()]
        datos = datos.unstack()
        datos = datos.reindex(fecha=np.concatenate((datos[_('fecha')].values, np.array(pd.to_datetime(nuevas_fechas)))))
        datos = datos.sortby(_('fecha'))

        return datos.interpolate_na(_('fecha')).stack(n=[_('fecha'), _('lugar')])


def _gen_fuente(fnt, nombre=None, lugares=None, fechas=None):
    if isinstance(fnt, pd.DataFrame):
        return FuentePandas(fnt, nombre or 'pandas', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, dict):
        return FuenteDic(fnt, nombre or 'dic', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, xr.Dataset):
        return FuenteBaseXarray(fnt, nombre or 'xarray', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, xr.DataArray):
        return FuenteVarXarray(fnt, nombre or 'xarray', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, str):
        ext = os.path.splitext(fnt)[1]

        if ext == '.csv':
            return FuenteCSV(fnt, lugares=lugares, fechas=fechas)
        else:
            raise ValueError(_('Formato de base de datos "{}" no reconocido.').format(ext))

    return fnt
