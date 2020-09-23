from typing import Optional, Generator

import xarray as xr

from .resultados import Resultados
from .tiempo import Tiempo
from .utils import EJE_TIEMPO


class Rebanada(object):
    def __init__(
            símismo,
            n_pasos: int,
            tiempo: Tiempo,
            resultados: Resultados,
            externos: Optional[xr.Dataset] = None
    ):
        símismo.n_pasos = n_pasos
        símismo.resultados = resultados
        símismo.variables = resultados.variables
        símismo.externos = externos

        símismo.eje = tiempo.eje[tiempo.paso + 1, tiempo.paso + 1 + n_pasos]

    def recibir(símismo, datos: xr.Dataset):
        if EJE_TIEMPO not in datos.coords:
            datos = datos.set_coords([EJE_TIEMPO, *datos.coords])

        símismo.resultados.recibir(datos)

    def __iter__(símismo) -> Generator["PasoRebanada"]:
        for i in range(símismo.n_pasos):
            yield PasoRebanada(símismo, i)


class PasoRebanada(object):
    def __init__(símismo, rebanada: Rebanada, i: int):
        símismo.rebanada = rebanada
        símismo.i = i

        símismo.externos = rebanada.externos.isel[EJE_TIEMPO: i] if rebanada.externos else None

    def recibir(símismo, datos: xr.Dataset):
        if EJE_TIEMPO not in datos:
            datos[EJE_TIEMPO] = [símismo.rebanada.eje[símismo.i]]

        if EJE_TIEMPO not in datos.dims:
            datos = datos.expand_dims({EJE_TIEMPO: 1})

        símismo.rebanada.recibir(datos)
