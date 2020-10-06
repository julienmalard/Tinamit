from tinamit.hilo import Hilo
from tinamit.modelo import Modelo
from .extras import Extra


class Externos(Extra):
    def __init__(símismo, iniciales=None, temporales=None):
        símismo.iniciales = iniciales or []
        símismo.temporales = temporales or {}
        super().__init__(ModeloExterno())


class ModeloExterno(Modelo):

    @property
    def hilo(símismo) -> Type[Hilo]:
        return HiloExterno


class HiloExterno(Hilo):
    pass
