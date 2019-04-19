import numpy as np
import pandas as pd
import xarray as xr

from tinamit.config import _
from .tiempo import TiempoCalendario
from .var import Variable


class Extern(object):
    def __init__(símismo, vals_vars, interpol=True):
        símismo.interpol = interpol
        símismo._vals = vals_vars

    def obt_vals_t(símismo, t, var=None):
        vals = símismo._vals

        if var is not None:
            if isinstance(var, (str, Variable)):
                var = [var]
            vals = {vr: vl for vr, vl in vals if vr in var}

        vals = {vr: símismo._obt_a_t(vl, t, símismo.interpol) for vr, vl in vals.items()}

        return {vr: vl for vr, vl in vals.items() if not np.all(np.isnan(vl))}

    @staticmethod
    def _obt_a_t(m_xr, t, interpol):
        tiempo_xr = m_xr[_('tiempo')]
        if np.issubdtype(tiempo_xr.dtype, np.datetime64):
            if not isinstance(t, TiempoCalendario):
                raise TypeError(_(
                    'Solamente se pueden utilizar datos caléndricos con una simulación con fecha inicial.'
                ))
            i = t.fecha()
        else:
            i = t.í * t.tmñ_paso  # para hacer: ¿más elegante?
        if interpol and len(tiempo_xr) > 1:
            return m_xr.interp(**{_('tiempo'): i}).values
        try:
            return m_xr.sel(**{_('tiempo'): i}).values if not isinstance(i, int) else m_xr[i].values
        except (KeyError, IndexError):
            return np.nan


def gen_extern(datos, interpol=True):
    if isinstance(datos, Extern):
        return Extern

    if isinstance(datos, pd.DataFrame):
        datos = datos.to_xarray().rename({'index': _('tiempo')})

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
            coords={_('tiempo'): [0]},
            dims=[_('tiempo'), *('x_' + str(i) for i in range(len(val.shape)))]
        )
