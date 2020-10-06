from __future__ import annotations

from typing import Union, Optional, List, Dict

import trio

from conectado import Conectado
from resultados import Resultados
from tiempo import EspecTiempo
from tinamit.modelo import Modelo
from variables import Variable


class Extra(object):

    def __init__(
            símismo,
            modelos: Union[Modelo, List[Modelo]]
    ):
        símismo.modelos = [modelos] if isinstance(modelos, Modelo) else modelos

    def simular(
            símismo,
            modelo: Modelo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ) -> Dict[str, Resultados]:

        return trio.run(símismo.simular_async, modelo, tiempo, variables)

    async def simular_async(
            símismo,
            modelo: Modelo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ) -> Dict[str, Resultados]:

        modelo = Conectado(nombre='', modelos=[modelo, *símismo.modelos])
        return await modelo.simular_asinc(tiempo, variables)

    def __add__(símismo, otro: Extra):
        return Extra([*símismo.modelos, *otro.modelos])
