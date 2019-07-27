import os

import numpy as np
import pandas as pd
import xarray as xr
from tinamit.config import _

from .fuente import FuentePandas, FuenteDic, FuenteVarXarray, FuenteBaseXarray, FuenteCSV, Fuente


class BD(object):
    """
    Una base de datos combina varias :class:`~tinamit.datos.fuente.Fuente`.
    """
    def __init__(símismo, fuentes):
        """

        Parameters
        ----------
        fuentes: Fuente or list
            Las fuentes de la base de datos.
        """
        fuentes = [fuentes] if not isinstance(fuentes, (list, tuple)) else fuentes
        símismo.fuentes = [_gen_fuente(f) for f in fuentes]
        símismo.variables = list(set((v for f in símismo.fuentes for v in f.variables)))

        símismo.lugares = np.unique(np.concatenate([np.unique(fnt.lugares) for fnt in símismo.fuentes]))
        símismo.fechas = np.unique(np.concatenate([np.unique(fnt.fechas) for fnt in símismo.fuentes]))

    def obt_vals(símismo, vars_interés=None, lugares=None, fechas=None):
        """
        Devuelve los valores de unos variables de interés.

        Parameters
        ----------
        vars_interés: str or list
            Los variables de interés.
        lugares: list
            Lugares de interés.
        fechas: tuple or list

        Returns
        -------
        xr.DataArray, xr.Dataset
            ``xr.DataArray`` si ``vars_interés`` es ``str``, ``xr.Dataset`` si ``vars_interés`` es ``list``.
        """
        vr_único = False
        if isinstance(vars_interés, str):
            vars_interés = [vars_interés]
            vr_único = True

        if vars_interés is None:
            vars_interés = símismo.variables

        l_vals_fnts = [
            f.obt_vals(vars_interés=vars_interés, lugares=lugares, fechas=fechas) for f in símismo.fuentes
        ]
        l_vals_fnts = [v for v in l_vals_fnts if v.data_vars]
        vals = xr.merge(l_vals_fnts)

        return vals[vars_interés[0]] if vr_único else vals

    def interpolar(símismo, vars_interés, lugares=None, fechas=None, extrap=False):
        """
        Interpola datos por fecha, tomando el lugar en cuenta.

        Parameters
        ----------
        vars_interés: str or list
            Los variables de interés.
        lugares: list
            Lugares de interés.
        fechas: list or str or datetime.datetime
            Las fechas de interés.
        extrap: bool
            Si hay que extrapolar también.

        Returns
        -------
        xr.DataArray, xr.Dataset
            ``xr.DataArray`` si ``vars_interés`` es ``str``, ``xr.Dataset`` si ``vars_interés`` es ``list``.
        """

        datos = símismo.obt_vals(vars_interés=vars_interés, lugares=lugares)
        if datos['n'].size:
            datos = _interpolar_xr(datos, fechas=fechas)

            if extrap:
                datos = datos.bfill(_('fecha'))
                datos = datos.ffill(_('fecha'))

            return datos


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


def _interpolar_xr(m, fechas=None):
    m = m.unstack()
    if m.sizes[_('fecha')] > 1:

        m = m.interpolate_na(_('fecha')).fillna(m)
        if fechas is not None:
            fechas = [fechas] if not isinstance(fechas, (tuple, list)) else fechas
            m = m.interp(
                {_('fecha'): pd.DatetimeIndex(fechas)}
            ).fillna(m)
    m = m.dropna(_('lugar'), how='all')
    return m.stack(n=[_('lugar'), _('fecha')])
