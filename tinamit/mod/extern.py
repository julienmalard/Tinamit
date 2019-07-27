import datetime as ft

import numpy as np
import pandas as pd
import xarray as xr
from tinamit.config import _
from tinamit.tiempo.tiempo import TiempoCalendario, Tiempo

from .var import Variable


class Extern(object):
    """
    Datos externos para simulaciones.
    """

    def __init__(símismo, vals_vars, interpol=True):
        """

        Parameters
        ----------
        vals_vars: dict[str, xr.DataArray]
            Diccionario de los valores de los variables.
        interpol: bool
            Si se puede interpolar los datos.
        """
        símismo.interpol = interpol
        símismo._vals = vals_vars

    def obt_vals(símismo, t, var=None):
        """
        Devuelve los valores de uno o más variables.

        Parameters
        ----------
        t
            El tiempo de interés.
        var: str or Variable or list
            Los variables de interés.

        Returns
        -------
        dict[str, xr.DataArray]
        """
        vals = símismo._vals

        if var is not None:
            if isinstance(var, (str, Variable)):
                var = [var]
            vals = {vr: vl for vr, vl in vals.items() if vr in var}

        vals = {vr: símismo._obt_a_t(vl, t, símismo.interpol) for vr, vl in vals.items()}

        return {vr: vl for vr, vl in vals.items() if not np.all(np.isnan(vl))}

    @staticmethod
    def _obt_a_t(m_xr, t, interpol):
        m_xr = m_xr.unstack()

        t = relativizar_eje(m_xr, t)
        if interpol and m_xr.sizes[_('fecha')] > 1:
            return m_xr.interp(**{_('fecha'): t}).dropna(_('fecha'))
        try:
            return m_xr.reindex({_('fecha'): t}).dropna(_('fecha'))
        except (KeyError, IndexError):
            return np.nan


def gen_extern(datos, interpol=True):
    """
    Transforma datos en objeto :class:`~tinamit.extern.Extern`.

    Parameters
    ----------
    datos: Extern, pd.DataFrame or xr.Dataset or dict
        Los datos.
    interpol: bool
        Si se pueden interpolar los datos.

    Returns
    -------
    Extern

    """
    if isinstance(datos, Extern):
        return datos

    if isinstance(datos, pd.DataFrame):
        datos = datos.to_xarray().rename({'index': _('fecha')})

    if isinstance(datos, xr.Dataset):
        return Extern({vr: datos[vr] for vr in datos.data_vars}, interpol)
    elif isinstance(datos, dict):
        return Extern({vr: _a_matr_xr(vl) for vr, vl in datos.items()})


def _a_matr_xr(val):
    if isinstance(val, xr.DataArray):
        return val
    else:
        if not isinstance(val, np.ndarray):
            val = np.array([val])
        return xr.DataArray(
            val.reshape((1, *val.shape)),
            coords={_('fecha'): [0]},
            dims=[_('fecha'), *('x_' + str(i) for i in range(len(val.shape)))]
        )


def relativizar_eje(ref, otro):
    índ_ref = _obt_índ(ref)
    if isinstance(otro, TiempoCalendario):
        índ_otro = pd.to_datetime([otro.fecha()]) if isinstance(índ_ref, pd.DatetimeIndex) else pd.Index([otro.í])
    elif isinstance(otro, Tiempo):
        índ_otro = pd.Index([otro.í])
    else:
        índ_otro = _obt_índ(otro)

    if isinstance(índ_ref, pd.DatetimeIndex):
        if isinstance(índ_otro, pd.DatetimeIndex):
            return índ_otro
        raise TypeError

    if isinstance(índ_otro, pd.DatetimeIndex):
        return pd.to_datetime(índ_ref, unit='D', origin=índ_otro[0])

    return índ_otro


def _obt_índ(dts):
    if isinstance(dts, pd.Index):
        return dts
    if isinstance(dts, pd.DataFrame):
        return dts.index
    if isinstance(dts, (xr.Dataset, xr.DataArray)):
        return dts.to_pandas().index
    if isinstance(dts, (float, int)):
        return pd.Index([dts])
    if isinstance(dts, np.ndarray):
        return pd.Index(dts)
    if isinstance(dts, (np.datetime64, str, ft.datetime, ft.date)):
        return pd.to_datetime([dts])

    raise TypeError(type(dts))
