from typing import Type, Union, Dict, Optional, List

from .contexto import obtener_hilos
from .hilo import Hilo
from .rebanada import Rebanada
from .resultados import Resultados
from .simul import Simulación
from .tiempo import gen_tiempo, Tiempo
from .variables import Variable


class SimulModelo(Hilo):
    def __init__(símismo, modelo: "Modelo", tiempo: Tiempo):
        símismo.modelo = modelo
        super().__init__(nombre=str(modelo), tiempo=tiempo)

    async def incr(símismo, rebanada: Rebanada):
        raise NotImplementedError


class Modelo(object):

    def __init__(símismo, nombre: str, variables: Dict[str, Variable]):
        símismo.nombre = nombre
        símismo.variables = variables

    def iniciar(
            símismo,
            tiempo: Union[int, Tiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ):
        tiempo = gen_tiempo(tiempo)
        otros_hilos = obtener_hilos(tiempo)

        return Simulación(
            hilos=[*símismo.hilos(tiempo), *otros_hilos],
            resultados=símismo.gen_resultados(tiempo, variables),
        )

    def hilos(símismo, tiempo: Tiempo):
        return [símismo.simulador(símismo, tiempo)]

    def simular(símismo, tiempo: Union[int, Tiempo], resultados=None):
        return símismo.iniciar(tiempo, resultados).simular()

    def gen_resultados(símismo, tiempo: Tiempo, variables: Optional[List[Union[str, Variable]]] = None):
        variables = variables or list(símismo.variables.values())
        variables = [vr if isinstance(vr, Variable) else símismo.variables[vr] for vr in variables]

        return Resultados(variables=variables, tiempo=tiempo)

    @property
    def simulador(símismo) -> Type[SimulModelo]:
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre
