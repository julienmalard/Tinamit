from typing import Type, Union

from fnt.tinamit3.modelo import Modelo, SimulModelo
from fnt.tinamit3.tiempo import UnidTiempo


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
