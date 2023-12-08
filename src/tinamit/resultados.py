from typing import Iterable

import numpy as np
import xarray as xr

from .tiempo import Tiempo
from .utils import EJE_TIEMPO
from .variables import Variable


class Resultados(object):
    def __init__(símismo, variables: Iterable[Variable], tiempo: Tiempo):
        símismo.variables = variables

        símismo.valores = xr.Dataset({
            str(vr): xr.DataArray(
                np.nan,
                coords={EJE_TIEMPO: tiempo.eje, **vr.coords},
                dims=[EJE_TIEMPO, *vr.dims]
            ) for vr in símismo.variables
        })

    def recibir(símismo, datos: xr.Dataset):
        símismo.valores = símismo.valores.fillna(datos)

    @property
    def completo(símismo):
        faltan = símismo.valores.isnull().any()
        return not any(faltan[str(vr)] for vr in símismo.variables)

