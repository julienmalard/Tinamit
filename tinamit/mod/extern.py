import numpy as np
import pandas as pd
import xarray as xr

from tinamit.config import _
from .tiempo import Tiempo
from .var import Variable


class Extern(object):
    def __init__(símismo, vals_vars, interpol=True):
        símismo.interpol = interpol
        símismo._vals = vals_vars

    def obt_vals(símismo, t, var=None):
        vals = símismo._vals

        if var is not None:
            if isinstance(var, (str, Variable)):
                var = [var]
            vals = {vr: vl for vr, vl in vals.items() if vr in var}

        vals = {vr: símismo._obt_a_t(vl, t, símismo.interpol) for vr, vl in vals.items()}

        return {vr: vl for vr, vl in vals.items() if not np.all(np.isnan(vl))}

    @staticmethod
    def _obt_a_t(m_xr, t, interpol):
        tiempo_xr = m_xr[_('fecha')]
        if np.issubdtype(tiempo_xr.dtype, np.datetime64):
            if isinstance(t, Tiempo):
                f = t.fecha()
            elif isinstance(t, tuple):
                f = t[1]
            else:
                f = t
            if interpol and len(tiempo_xr) > 1:
                return m_xr.interp(**{_('fecha'): f})
            try:
                return m_xr.sel(**{_('fecha'): f})
            except (KeyError, IndexError):
                return np.nan
        if isinstance(t, Tiempo):
            i = t.í
        elif isinstance(t, tuple):
            i = t[0]
        elif isinstance(t, (int, float)):
            i = t
        else:
            i = [j for j in t if j in m_xr[_('fecha')]]
        if interpol and len(tiempo_xr) > 1:
            return m_xr.interp(**{_('fecha'): i})
        try:
            return m_xr[i]
        except (KeyError, IndexError):
            return np.nan


def gen_extern(datos, interpol=True):
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
