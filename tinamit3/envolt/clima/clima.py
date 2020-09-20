from tinamit3.modelo import Modelo
from tinamit3.simul import Simulación

class Clima(Modelo):

    def simulador(símismo):
        return SimulaciónClima(símismo)

class SimulaciónClima(Simulación):
    pass