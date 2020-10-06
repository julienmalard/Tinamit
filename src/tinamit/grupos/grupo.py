from itertools import product
from typing import Union, Optional, List, Dict

import trio

from tinamit.extras.clima import Clima
from tinamit.extras.externos import Externos
from tinamit.extras.extras import Extra
from tinamit.modelo import Modelo
from tinamit.resultados import Resultados
from tinamit.tiempo import EspecTiempo
from tinamit.variables import Variable


class Grupo(object):
    def __init__(símismo, corridas: Dict[str, List[Extra]]):
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

        async def _simular(nmb: str, extras: Extra):
            res[nmb] = await extras.simular_async(
                modelo,
                tiempo=tiempo,
                variables=variables
            )

        async with trio.open_nursery() as grupo:
            for nombre, corrida in símismo.corridas.items():
                grupo.start_soon(_simular, nombre, sum(corrida))

        return res


class GrupoLista(Grupo):
    def __init__(símismo, corridas: List[Extra]):
        d_corridas = {str(extra): extra for extra in corridas}
        super().__init__(d_corridas)


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
