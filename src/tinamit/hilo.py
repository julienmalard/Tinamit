from __future__ import annotations

from typing import Dict, List, Optional, Tuple

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
            integ_tiempo: str
    ):
        símismo.hilo_fuente = hilo_fuente
        símismo.var_fuente = var_fuente
        símismo.var_recep = var_recep
        símismo.transf = transf
        símismo.integ_tiempo = integ_tiempo

        símismo.anterior: Optional[pd.Timestamp] = None

    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        remuestreo = res.resample(indexer={EJE_TIEMPO: tiempo.unids.unid_retallo})
        res = getattr(remuestreo, símismo.integ_tiempo)().rename(str(símismo.var_recep))

        return símismo.transf(res) if símismo.transf else res

    def próximo_tiempo(símismo) -> pd.Timestamp:
        raise NotImplementedError


class RequísitoInicPaso(Requísito):
    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        f_inic = símismo.anterior or tiempo.eje[0] - pd.Timedelta(tiempo.unids.unid_retallo)
        f_final = tiempo.ahora + pd.Timedelta(str(tiempo.unids.n * max(0, n_pasos - 1)) + tiempo.unids.unid_freq_pd)
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
        f_inic = tiempo.ahora if símismo.anterior else tiempo.eje[0] - pd.Timedelta(tiempo.unids.unid_retallo)
        f_final = tiempo.eje[tiempo.paso + n_pasos]
        máscara = np.logical_and(res[EJE_TIEMPO] > f_inic, res[EJE_TIEMPO] <= f_final)
        res = res.loc[máscara]
        res[EJE_TIEMPO] = res[EJE_TIEMPO] - pd.Timedelta(tiempo.unids.unid_retallo)

        símismo.anterior = f_final
        return super().recortar(tiempo, n_pasos, res=res)

    def próximo_tiempo(símismo) -> pd.Timestamp:
        return símismo.hilo_fuente.tiempo.ahora


class RequísitoInicial(Requísito):
    def recortar(símismo, tiempo: Tiempo, n_pasos: int, res: xr.DataArray) -> xr.DataArray:
        f_inic = tiempo.eje[0]
        f_final = tiempo.eje[-1]
        return f_inic, f_final
