from .contexto import Contexto
from .hilo import Hilo
from .tiempo import Tiempo


class Iniciales(Contexto):
    def hilo(símismo, tiempo: Tiempo) -> Hilo:
        return HiloIniciales(tiempo)


class Externos(Contexto):
    def hilo(símismo, tiempo: Tiempo) -> Hilo:
        return HiloExternos(tiempo)


class HiloExternos(Hilo):
    pass


class HiloIniciales(Hilo):
    pass
