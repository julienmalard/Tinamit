from typing import List

import numpy as np
import xarray as xr

from .tiempo import Tiempo
from .utils import EJE_TIEMPO
from .variables import Variable


class Resultados(object):
    def __init__(símismo, variables: List[Variable], tiempo: Tiempo):
        símismo.variables = variables

        símismo.valores = xr.Dataset({
            str(vr): xr.DataArray(
                np.nan,
                coords={EJE_TIEMPO: tiempo.eje, **vr.coords},
                dims=[EJE_TIEMPO, *vr.dims]
            ) for vr in variables
        })

    def recibir(símismo, datos: xr.Dataset):
        símismo.valores.update(datos)

    @property
    def completo(símismo):
        faltan = símismo.valores.isnull().any()
        return not any(faltan[vr] for vr in símismo.variables)


class Transformador(object):
    def __init__(símismo, f):
        símismo.f = f

    def __call__(símismo, val):
        return símismo.f(val)

    def __add__(símismo, otro):
        f = otro.f if isinstance(otro, Transformador) else otro
        return Transformador(f=lambda x: símismo.f(f(x)))


class RenombrarEjes(Transformador):
    def __init__(símismo, dic_nombres):
        super().__init__(f=lambda x: x.rename_dims(dic_nombres))


class FactorConv(Transformador):
    def __init__(símismo, factor):
        super().__init__(f=lambda x: x * factor)
