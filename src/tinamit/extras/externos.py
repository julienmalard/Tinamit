from typing import Type

from tinamit.hilo import Hilo
from .extras import Extra, ModeloExtra


class Externos(Extra):
    def __init__(
            símismo,
            iniciales=None,
            temporales=None,
            nombre: str = 'externos'
    ):
        símismo.iniciales = iniciales or []
        símismo.temporales = temporales or {}
        super().__init__(nombre, modelos=ModeloExterno())


class ModeloExterno(ModeloExtra):
    @property
    def hilo(símismo) -> Type[Hilo]:
        return HiloExterno


class HiloExterno(Hilo):
    pass
