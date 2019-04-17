import numpy as np
import pandas as pd
import xarray as xr

from tinamit.config import _


class Extern(object):
    def __init__(símismo, extern_vars, interpol=True):
        símismo.interpol = interpol
        símismo._vars = extern_vars


def gen_extern(datos, interpol=True):
    if isinstance(datos, Extern):
        return Extern

    if isinstance(datos, pd.DataFrame):
        datos = datos.to_xarray()

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
