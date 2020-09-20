from typing import List

from .hilo import Hilo
from .tiempo import Tiempo


class Contexto(object):
    def hilo(símismo, tiempo: Tiempo) -> Hilo:
        raise NotImplementedError

    def __enter__(símismo):
        _contexto.append(símismo)

    def __exit__(símismo):
        _contexto.remove(símismo)


_contexto: List[Contexto] = []


def obtener_hilos(tiempo: Tiempo):
    return [c.hilo(tiempo) for c in _contexto]
