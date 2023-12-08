from __future__ import annotations

from numbers import Number
from typing import Type, Union, Dict, Optional, List, Set

from .conex import ConexiónVars
from .hilo import Hilo
from .instalador import Instalador
from .rebanada import Rebanada
from .resultados import Resultados, Transformador
from .simul import Simulación
from .tiempo import gen_tiempo, Tiempo, EspecTiempo, UnidTiempo
from .variables import Variable


class SimulModelo(Hilo):
    def __init__(símismo, modelo: Modelo, tiempo: Tiempo):
        símismo.modelo = modelo
        super().__init__(
            nombre=str(modelo),
            unid_tiempo=modelo.unid_tiempo,
            tiempo=tiempo,
            variables=modelo.variables
        )

    async def incr(símismo, rebanada: Rebanada):
        await super().incr(rebanada)


class Modelo(object):
    descargas: Optional[str, Instalador] = None

    def __init__(símismo, nombre: str, variables: Dict[str, Variable], unid_tiempo: Union[str, UnidTiempo]):
        símismo.nombre = nombre
        símismo.variables = variables
        símismo.unid_tiempo = unid_tiempo if isinstance(unid_tiempo, UnidTiempo) else UnidTiempo(unid_tiempo)

    def iniciar(
            símismo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None,
    ):

        tiempo = gen_tiempo(tiempo, símismo.unid_tiempo)

        hilos = símismo.hilos(tiempo)

        dic_variables = símismo.resolver_variables(variables, hilos)

        return Simulación(
            hilos=hilos,
            unid_tiempo=símismo.unid_tiempo,
            resultados={
                str(h): Resultados(dic_variables[str(h)], h.tiempo) for h in hilos
            }
        )

    def hilos(símismo, tiempo: Tiempo) -> List[Hilo]:
        hilo = símismo.hilo(símismo, tiempo)
        return [hilo]

    def simular(
            símismo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ) -> Dict[str, Resultados]:

        return símismo.iniciar(tiempo, variables).simular()

    async def simular_asinc(
            símismo,
            tiempo: Union[int, EspecTiempo],
            variables: Optional[List[Union[str, Variable]]] = None
    ) -> Dict[str, Resultados]:

        simul = símismo.iniciar(tiempo, variables)
        return await simul.simular_asinc()

    def resolver_variables(
            símismo,
            variables: List[Union[str, Variable]],
            hilos: List[Hilo]
    ) -> Dict[str, Set[Variable]]:

        variables = variables or list(símismo.variables.values())

        for h in hilos:
            variables += [req.var_fuente for req in h.requísitos]

        resueltos = {str(h): set() for h in hilos}
        for vr in variables:
            if isinstance(vr, Variable):
                hilo = vr.modelo
            else:
                try:
                    vr, hilo = next(
                        (v, h) for h in hilos for v in h.variables.values() if str(v) == str(vr)
                    )
                except StopIteration:
                    raise ValueError('Variable {} no encontrado'.format(vr))

            resueltos[str(hilo)].add(vr)
        return resueltos

    def conectar_clima(
            símismo,
            var: Union[str, Variable],
            var_clima: Union[str, Variable],
            transf: Optional[Union[Transformador, Number]] = None,
            integ_tiempo: str = "mean"
    ):
        símismo.conex.append(ConexiónVars(
            de=var_clima, a=var, modelo_de='Clima', modelo_a=str(símismo),
            transf=transf, integ_tiempo=integ_tiempo
        ))

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        raise NotImplementedError

    def __contains__(símismo, itema):
        return str(itema) in símismo.variables

    def __str__(símismo):
        return símismo.nombre
