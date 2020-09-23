from itertools import product
from typing import Union, Optional, List, Dict

import trio

from tinamit3.clima import Clima
from tinamit3.externos import Externos
from tinamit3.modelo import Modelo
from tinamit3.resultados import Resultados
from tinamit3.tiempo import EspecTiempo
from tinamit3.variables import Variable


class Grupo(object):
    def __init__(símismo, corridas: Dict[str, List]):
        símismo.corridas = corridas

    def simular(
            símismo,
            modelo: Modelo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ) -> Dict[str, Dict[str, Resultados]]:

        return trio.run(símismo.simular_asinc(modelo, tiempo, variables))

    async def simular_asinc(
            símismo,
            modelo: Modelo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ) -> Dict[str, Dict[str, Resultados]]:
        res = {}

        async def _simular(nmb: str, crd: List):
            simul = modelo.iniciar(tiempo, variables=variables, extras=crd)
            res[nmb] = await simul.simular_asinc()

        async with trio.open_nursery() as grupo:
            for nombre, corrida in símismo.corridas.items():
                grupo.start_soon(_simular, nombre, corrida)

        return res


class GrupoCombinador(Grupo):
    def __init__(
            símismo,
            externos: Optional[List[Externos]] = None,
            climas: Optional[List[Clima]] = None
    ):
        externos = externos or []
        climas = climas or []
        super().__init__({
            f'{ex} {cl}': [ex, cl] for ex, cl in product(externos, climas)
        })
