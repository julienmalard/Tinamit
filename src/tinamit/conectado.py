from typing import List, Type, Dict, Iterable

from tinamit.conex import ConexiónVars
from tinamit.hilo import Hilo
from tinamit.modelo import Modelo, SimulModelo
from tinamit.rebanada import Rebanada
from tinamit.tiempo import Tiempo, calc_tiempo_común


class Conectado(Modelo):
    def __init__(símismo, nombre: str, modelos: Iterable[Modelo], conex=None):
        símismo.modelos: Dict[str, Modelo] = {str(m): m for m in modelos}

        super().__init__(
            nombre,
            variables={f'{m}.{vr}': vr for m in símismo.modelos.values() for vr in m.variables.values()},
            unid_tiempo=calc_tiempo_común([m.unid_tiempo for m in símismo.modelos.values()])
        )

        símismo.conex: List[ConexiónVars] = símismo._validar_conex(conex or [])

    def hilos(símismo, tiempo: Tiempo):
        hilos = [h for mod in símismo.modelos.values() for h in mod.hilos(tiempo)]
        símismo._estab_reqs(hilos)
        return hilos

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulConectado

    def _validar_conex(símismo, conex: List[ConexiónVars]):
        for cnx in conex:
            for m in [cnx.modelo_a, cnx.modelo_de]:
                if m not in símismo.modelos:
                    raise ValueError('Modelo {} no definido.'.format(m))
            for m, v in zip([cnx.modelo_a, cnx.modelo_de], [cnx.a, cnx.de]):
                if v not in símismo.modelos[m]:
                    raise ValueError('Variable {v} no existe en modelo {m}'.format(v=v, m=m))
        return conex

    def _estab_reqs(símismo, hilos: List[Hilo]):
        for cnx in símismo.conex:
            hilo = next(h for h in hilos if h.nombre == cnx.modelo_a)
            hilo_fuente = next(h for h in hilos if h.nombre == cnx.modelo_de)
            hilo.requiere(cnx.clase_requísito(
                hilo_fuente=hilo_fuente,
                var_fuente=hilo_fuente.variables[cnx.de],
                var_recep=hilo.variables[cnx.a],
                transf=cnx.transf,
                integ_tiempo=cnx.integ_tiempo
            ))


class SimulConectado(SimulModelo):
    async def incr(símismo, rebanada: Rebanada):
        await super().incr(rebanada)  # Incremento ya implementado con inclusión recursiva de hilos en `Conectado`
