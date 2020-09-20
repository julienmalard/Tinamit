from typing import Iterable, Union

from .rebanada import Rebanada
from .tiempo import Tiempo


class Hilo(object):
    def __init__(símismo, nombre: str, tiempo: Tiempo):
        símismo.nombre = nombre
        símismo.tiempo = tiempo
        símismo.dependencias = set()

    async def iniciar(símismo):
        pass

    async def incr(símismo, rebanada: Rebanada):
        pass

    async def cerrar(símismo):
        pass

    def depiende_de(símismo, dependencia: Union[Iterable, "Hilo"]):
        dependencias = dependencia if isinstance(dependencia, Iterable) else [dependencia]
        símismo.dependencias = símismo.dependencias.union(dependencias)

    def próximo_paso(símismo) -> int:
        return min([
            símismo.tiempo.n_pasos,
            *[h.paso + 1 for h in símismo.dependencias]
        ])

    def __str__(símismo):
        return símismo.nombre
