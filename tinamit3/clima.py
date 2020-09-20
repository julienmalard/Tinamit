from numbers import Number

from .contexto import Contexto
from .hilo import Hilo
from .tiempo import Tiempo


class Clima(Contexto):
    def __init__(símismo, lat: Number, long: Number, elev: Number, escenario: str = '8.5', fuentes=None):
        símismo.coords = (lat, long, elev)
        símismo.escenario = escenario
        símismo.fuentes = fuentes

    def hilo(símismo, tiempo: Tiempo) -> Hilo:
        return HiloClima(tiempo)


class HiloClima(Hilo):
    pass
