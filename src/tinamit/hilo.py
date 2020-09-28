from __future__ import annotations

from typing import Dict, List, Optional

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
        símismo.nombre = nombre
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

    def próximo_paso(símismo) -> int:
        return min([
            símismo.tiempo.n_pasos,
            *[h.paso + 1 for h in símismo.dependencias]
        ])

    @property
    def dependencias(símismo):
        return {r.hilo for r in símismo.requísitos}

    def __str__(símismo):
        return símismo.nombre


class Requísito(object):
    def __init__(
            símismo,
            hilo: Hilo,
            var_fuente: Variable,
            var_recep: Variable,
            transf: Optional[Transformador] = None,
            integ_tiempo: str = "sum"
    ):
        símismo.hilo = hilo
        símismo.var_fuente = var_fuente
        símismo.var_recep = var_recep
        símismo.transf = transf
        símismo.integ_tiempo = integ_tiempo
