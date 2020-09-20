from collections import Counter
from typing import Iterable, List, Dict, Optional

import trio

from .hilo import Hilo
from .rebanada import Rebanada
from .resultados import Resultados
from .tiempo import conv_tiempo, calc_tiempo_común


class Simulación(object):
    def __init__(símismo, hilos: Iterable[Hilo], resultados: Resultados):
        dups = [nmbr for nmbr, i in Counter([str(h) for h in hilos]).items() if i > 1]
        if dups:
            raise ValueError("Nombres de modelos duplicados:\n\t{}".format("\n\t".join(dups)))

        símismo.hilos: Dict[str, Hilo] = {str(h): h for h in hilos}
        símismo.resultados = resultados
        símismo.unid_tiempo = calc_tiempo_común([h.tiempo.unids for h in hilos])

    def simular(símismo):
        return trio.run(símismo.simular_asinc())

    def iniciar(símismo):
        trio.run(símismo.iniciar_asinc)

    def incr(símismo, n_pasos):
        trio.run(símismo.incr_asinc, n_pasos)

    def correr(símismo):
        trio.run(símismo.correr_asinc)

    def cerrar(símismo):
        trio.run(símismo.cerrar_asinc())

    async def simular_asinc(símismo):
        await símismo.iniciar_asinc()
        await símismo.correr_asinc()
        await símismo.cerrar_asinc()

        return símismo.resultados

    async def iniciar_asinc(símismo):
        async with trio.open_nursery() as grupo:
            for h in símismo.hilos.values():
                grupo.start_soon(h.iniciar)

    async def incr_asinc(símismo, n_pasos: int, hilos: Optional[List[Hilo]] = None):
        hilos = hilos or símismo.hilos

        async with trio.open_nursery() as grupo:
            for h in hilos.values():
                n_pasos_h = conv_tiempo(n_pasos, de=símismo.unid_tiempo, a=h.tiempo.unids, t=h.tiempo.ahora)

                rebanada = Rebanada(
                    n_pasos=n_pasos_h,
                    variables=símismo.resultados.variables,
                    externos=
                )
                grupo.start_soon(h.incr, rebanada)

        return rebanada

    async def correr_asinc(símismo):
        t_ant = 0
        while q := símismo.quedan:
            t_máximo = max(h.próximo_paso() for h in q)
            próximos = [h for h in q if h.próximo_paso() == t_máximo]

            await símismo.incr_asinc(n_pasos=t_máximo - t_ant, hilos=próximos)
            t_ant = t_máximo

    async def cerrar_asinc(símismo):
        async with trio.open_nursery() as grupo:
            for h in símismo.hilos.values():
                grupo.start_soon(h.cerrar)

    @property
    def quedan(símismo) -> List[Hilo]:
        return [h for h in símismo.hilos.values() if h.tiempo.terminado]
