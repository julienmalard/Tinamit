from typing import Type, Dict, Union

from tinamit3.modelo import Modelo, SimulModelo
from tinamit3.tiempo import UnidTiempo
from tinamit3.variables import Variable


class Clima(Modelo):

    def __init__(
            símismo,
            unid_tiempo: Union[str, UnidTiempo]
    ):
        super().__init__(nombre='Clima', variables=variables, unid_tiempo=unid_tiempo)

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulaciónClima


class SimulaciónClima(SimulModelo):
    pass
