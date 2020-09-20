from typing import List, Dict, Optional, Generator

import numpy as np
import xarray as xr

from .resultados import Resultados
from .utils import EJE_TIEMPO
from .variables import Variable


class Rebanada(object):
    def __init__(
            símismo,
            n_pasos: int,
            variables: List[Variable],
            resultados: Resultados,
            ejes_vars: Optional[Dict[str, np.ndarray]] = None,
            externos: Optional[xr.Dataset] = None
    ):
        símismo.n_pasos = n_pasos
        símismo.variables = variables
        símismo.externos = externos
        símismo.resultados = resultados

        ejes_vars = ejes_vars or {}
        símismo.eje = np.array(sorted({símismo.n_pasos}.union({x for e in ejes_vars for x in e})))
        símismo.ejes_vars = {
            vr: ejes_vars[str(vr)] if str(vr) in ejes_vars else símismo.eje for vr in símismo.variables
        }

        símismo.vals = {
            str(vr): xr.DataArray(
                np.nan,
                dims=[EJE_TIEMPO, *vr.dims],
                coords={EJE_TIEMPO: símismo.ejes_vars[str(vr)], **vr.coords}
            ) for vr in símismo.variables
        }

    def recibir(símismo, datos: xr.Dataset):
        for vr, vl in datos.items():
            símismo.vals[vr].fillna(vl)

    def __iter__(símismo) -> Generator["PasoRebanada"]:
        for i in range(símismo.n_pasos):
            yield PasoRebanada(símismo, i)


class PasoRebanada(object):
    def __init__(símismo, rebanada: Rebanada, i: int):
        símismo.rebanada = rebanada
        símismo.externos = rebanada.externos.isel[EJE_TIEMPO: i]

    def recibir(símismo, datos: xr.Dataset):
        símismo.rebanada
