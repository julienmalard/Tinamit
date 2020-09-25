from numbers import Number
from typing import Type

from .contexto import Contexto
from .hilo import Hilo
from .tiempo import Tiempo


class Clima(Contexto):
    def __init__(símismo, lat: Number, long: Number, elev: Number, escenario: str = '8.5', fuentes=None):
        símismo.coords = (lat, long, elev)
        símismo.escenario = escenario
        símismo.fuentes = fuentes

    @property
    def hilo(símismo) -> Type[Hilo]:
        return HiloClima


class HiloClima(Hilo):
    pass
