from collections import Iterable
from typing import List, Type

from tinamit3.modelo import Modelo, SimulModelo
from tinamit3.rebanada import Rebanada
from tinamit3.tiempo import Tiempo


class Conectado(Modelo):
    def __init__(símismo, nombre: str, modelos: Iterable[Modelo], conex=None):
        símismo.modelos = modelos
        símismo.conex: List[ConexiónVars] = símismo._validar_conex(conex)

        super().__init__(nombre, variables={f'{m}.{vr}': vr for m in símismo.modelos for vr in m.variables})

    def hilos(símismo, tiempo: Tiempo):
        hilos = [h for mod in símismo.modelos for h in mod.hilos(tiempo)]
        for h in hilos:
            h.depiende_de([
                h2 for h2 in hilos if any(cnx.mod_de == h2.modelo and cnx.mod_a == h for cnx in símismo.conex)
            ])
        return hilos

    @property
    def simulador(símismo) -> Type[SimulModelo]:
        return SimulConectado

    def _validar_conex(símismo, conex):
        if conex is None:
            return []
        return conex


class ConexiónVars(object):
    def __init__(símismo, de, a, mod_de, mod_a, transf=None):
        símismo.de = de
        símismo.a = a
        símismo.mod_de = str(mod_de)
        símismo.mod_a = str(mod_a)
        símismo.transf = transf


class SimulConectado(SimulModelo):
    async def incr(símismo, rebanada: Rebanada):
        pass  # Incremento ya implementado con inclusión recursiva de hilos en `Conectado`
