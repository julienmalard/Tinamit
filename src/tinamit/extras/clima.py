from numbers import Number
from typing import Type

from tinamit.hilo import Hilo
from tinamit.modelo import Modelo
from .extras import Extra


class Clima(Extra):
    def __init__(
            símismo,
            lat: Number, long: Number,
            elev: Number,
            escenario: str = '8.5',
            fuentes=None
    ):
        símismo.coords = (lat, long, elev)
        símismo.escenario = escenario
        símismo.fuentes = fuentes
        super().__init__(modelos=ModeloClima())


class ModeloClima(Modelo):

    @property
    def hilo(símismo) -> Type[Hilo]:
        return HiloClima


class HiloClima(Hilo):
    pass
