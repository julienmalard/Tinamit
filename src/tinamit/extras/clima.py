from numbers import Number
from typing import Type

from tinamit.hilo import Hilo
from .extras import Extra, ModeloExtra


class Clima(Extra):
    def __init__(
            símismo,
            lat: Number, long: Number,
            elev: Number,
            escenario: str = '8.5',
            fuentes=None,
            nombre: str = 'clima'
    ):
        símismo.coords = (lat, long, elev)
        símismo.escenario = escenario
        símismo.fuentes = fuentes
        super().__init__(nombre, modelos=ModeloClima())


class ModeloClima(ModeloExtra):

    @property
    def hilo(símismo) -> Type[Hilo]:
        return HiloClima


class HiloClima(Hilo):
    pass
