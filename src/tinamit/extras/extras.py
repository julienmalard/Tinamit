from __future__ import annotations

from typing import Union, Optional, List, Dict, Type

import trio

from modelo import SimulModelo
from tinamit.conectado import Conectado
from tinamit.conex import ConexiónVars
from tinamit.modelo import Modelo
from tinamit.resultados import Resultados
from tinamit.tiempo import EspecTiempo
from tinamit.variables import Variable


class Extra(object):

    def __init__(
            símismo,
            nombre: str,
            modelos: Union[ModeloExtra, List[ModeloExtra]]
    ):
        símismo.nombre = nombre
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

        modelo_con = Conectado(
            nombre=símismo.nombre,
            modelos=[modelo, *símismo.modelos],
            conex=[m.gen_conex(modelo) for m in símismo.modelos]
        )
        return await modelo_con.simular_asinc(tiempo, variables)

    def __add__(símismo, otro: Extra):
        return Extra(nombre=f'{símismo} _ {otro}', modelos=[*símismo.modelos, *otro.modelos])


class ModeloExtra(Modelo):

    def gen_conex(símismo, modelo: Modelo) -> List[ConexiónVars]:
        raise NotImplementedError

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        raise NotImplementedError
