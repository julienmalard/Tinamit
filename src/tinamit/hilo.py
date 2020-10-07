from __future__ import annotations

from typing import Dict, List, Optional, Callable, Union

import numpy as np
import pandas as pd
import xarray as xr

from utils import EJE_TIEMPO
from .rebanada import Rebanada
from .resultados import Transformador
from .tiempo import Tiempo, UnidTiempo
from .variables import Variable


class Hilo(object):
    def __init__(
            símismo,
            nombre: str,
            unid_tiempo: UnidTiempo,
            tiempo: Tiempo,
            variables: Dict[str, Variable]
    ):
        símismo.nombre = nombre.replace('.', '_')
        símismo.tiempo = unid_tiempo.gen_tiempo(tiempo)
        símismo.variables = variables
        símismo.requísitos: List[Requísito] = []

    async def iniciar(símismo, rebanada: Rebanada):
        pass

    async def incr(símismo, rebanada: Rebanada):
        símismo.tiempo.incr(rebanada.n_pasos)

    async def cerrar(símismo):
        pass

    def requiere(símismo, requísito: Requísito):
        símismo.requísitos.append(requísito)

    def próximo_tiempo(símismo) -> pd.Timestamp:
        próximo_posible = min([
            símismo.tiempo.eje[-1],
            *[r.próximo_tiempo() for r in símismo.requísitos]
        ])
        return símismo.tiempo.eje[símismo.tiempo.eje <= próximo_posible][-1]

    @property
    def dependencias(símismo):
        return {r.hilo_fuente for r in símismo.requísitos}

    def __str__(símismo):
        return símismo.nombre


class Requísito(object):
    def __init__(
            símismo,
            hilo_fuente: Hilo,
            var_fuente: Variable,
            var_recep: Variable,
            transf: Optional[Transformador],
            integ_tiempo: Union[str, Callable]
    ):
        símismo.hilo_fuente = hilo_fuente
        símismo.var_fuente = var_fuente
        símismo.var_recep = var_recep
        símismo.transf = transf

        if isinstance(integ_tiempo, str):
            símismo.f_integ = lambda x: getattr(x, integ_tiempo)()
        else:
            símismo.f_integ = lambda x: x.reduce(integ_tiempo)

        símismo.anterior: Optional[pd.Timestamp] = None

    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        eje = tiempo.eje[tiempo.paso: tiempo.paso + max(1, n_pasos)]
        res = res.assign_coords({EJE_TIEMPO: [next(x for x in eje if f <= x) for f in res[EJE_TIEMPO]]})
        remuestreo = res.groupby(EJE_TIEMPO)
        integrado = símismo.f_integ(remuestreo).rename(str(símismo.var_recep))

        return símismo.transf(integrado) if símismo.transf else integrado

    @staticmethod
    def _ajustar_eje_t(res: xr.DataArray, dif: pd.DateOffset):
        # Necesario por incompatibilidad entre xarray[np.datetime64] y pd.DateOffset
        res[EJE_TIEMPO] = (pd.to_datetime(list(res[EJE_TIEMPO].values)) + dif).to_numpy()

    def próximo_tiempo(símismo) -> pd.Timestamp:
        raise NotImplementedError


class RequísitoInicPaso(Requísito):
    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        f_inic = símismo.anterior if símismo.anterior else tiempo.eje[0] - tiempo.unids.retallo
        f_final = tiempo.eje[tiempo.paso + max(n_pasos-1, 0)]
        máscara = np.logical_and(res[EJE_TIEMPO] > f_inic, res[EJE_TIEMPO] <= f_final)
        res = res.loc[máscara]

        if n_pasos:
            símismo.anterior = f_final

        return super().recortar(tiempo, n_pasos, res=res)

    def próximo_tiempo(símismo) -> pd.Timestamp:
        hilo = símismo.hilo_fuente
        return hilo.tiempo.ahora + 1 * hilo.tiempo.ahora.freq


class RequísitoContemporáneo(Requísito):
    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        f_inic = tiempo.ahora if símismo.anterior else tiempo.eje[0] - tiempo.unids.retallo
        f_final = tiempo.eje[tiempo.paso + n_pasos]
        máscara = np.logical_and(res[EJE_TIEMPO] > f_inic, res[EJE_TIEMPO] <= f_final)
        res = res.loc[máscara]
        símismo._ajustar_eje_t(res, -tiempo.unids.retallo)

        símismo.anterior = f_final
        return super().recortar(tiempo, n_pasos, res=res)

    def próximo_tiempo(símismo) -> pd.Timestamp:
        return símismo.hilo_fuente.tiempo.ahora


class RequísitoInicial(Requísito):
    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        f_inic = tiempo.eje[0]
        f_final = tiempo.eje[-1]
        return f_inic, f_final
