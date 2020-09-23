from collections import Iterable
from typing import List, Type, Dict

from tinamit3.conex import ConexiónVars
from tinamit3.hilo import Hilo
from tinamit3.modelo import Modelo, SimulModelo
from tinamit3.rebanada import Rebanada
from tinamit3.tiempo import Tiempo, calc_tiempo_común


class Conectado(Modelo):
    def __init__(símismo, nombre: str, modelos: Iterable[Modelo], conex=None):
        símismo.modelos: Dict[str, Modelo] = {str(m): m for m in modelos}

        super().__init__(
            nombre,
            variables={f'{m}.{vr}': vr for m in símismo.modelos.values() for vr in m.variables},
            unid_tiempo=calc_tiempo_común([m.unid_tiempo for m in símismo.modelos.values()])
        )
        símismo.conex += símismo._validar_conex(conex or [])

    def hilos(símismo, tiempo: Tiempo, otros: List[Hilo]):
        hilos = [h for mod in símismo.modelos.values() for h in mod.hilos(tiempo, otros)]
        return hilos

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulConectado

    def _validar_conex(símismo, conex: List[ConexiónVars]):
        for cnx in conex:
            for m in [cnx.modelo_a, cnx.modelo_de]:
                if m not in símismo.modelos:
                    raise ValueError('Modelo {} no definido.'.format(m))
            for v, m in zip([cnx.modelo_a, cnx.modelo_de], [cnx.a, cnx.de]):
                if v not in símismo.modelos[m]:
                    raise ValueError('Variable {v} no existe en modelo {m}'.format(v=v, m=m))
        return conex


class SimulConectado(SimulModelo):
    async def incr(símismo, rebanada: Rebanada):
        await super().incr(rebanada)  # Incremento ya implementado con inclusión recursiva de hilos en `Conectado`
