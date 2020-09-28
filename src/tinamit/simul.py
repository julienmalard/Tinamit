from collections import Counter
from typing import Iterable, List, Dict, Optional

import trio
import xarray as xr

from .hilo import Hilo
from .rebanada import Rebanada
from .resultados import Resultados
from .tiempo import conv_tiempo, UnidTiempo
from .utils import EJE_TIEMPO


class Simulación(object):
    def __init__(símismo, hilos: Iterable[Hilo], unid_tiempo: UnidTiempo, resultados: Dict[str, Resultados]):
        dups = [nmbr for nmbr, i in Counter([str(h) for h in hilos]).items() if i > 1]
        if dups:
            raise ValueError("Nombres de modelos duplicados:\n\t{}".format("\n\t".join(dups)))

        símismo.hilos: Dict[str, Hilo] = {str(h): h for h in hilos}
        símismo.resultados = resultados
        símismo.unid_tiempo = unid_tiempo

    def simular(símismo) -> Dict[str, Resultados]:
        return trio.run(símismo.simular_asinc)

    def iniciar(símismo):
        trio.run(símismo.iniciar_asinc)

    def incr(símismo, n_pasos):
        trio.run(símismo.incr_asinc, n_pasos)

    def correr(símismo):
        trio.run(símismo.correr_asinc)

    def cerrar(símismo):
        trio.run(símismo.cerrar_asinc)

    async def simular_asinc(símismo) -> Dict[str, Resultados]:
        await símismo.iniciar_asinc()
        await símismo.correr_asinc()
        await símismo.cerrar_asinc()

        return símismo.resultados

    async def iniciar_asinc(símismo):
        async with trio.open_nursery() as grupo:
            for h in símismo.hilos.values():
                rebanada = Rebanada(
                    n_pasos=0,
                    tiempo=h.tiempo,
                    resultados=símismo.resultados[str(h)],
                    externos=símismo._gen_externos(h, 0)
                )
                grupo.start_soon(h.iniciar, rebanada)

    async def incr_asinc(símismo, n_pasos: int, hilos: Optional[Dict[str, Hilo]] = None):
        hilos = hilos or símismo.hilos

        async with trio.open_nursery() as grupo:
            for h in hilos.values():
                n_pasos_h = conv_tiempo(n_pasos, de=símismo.unid_tiempo, a=h.tiempo.unids, t=h.tiempo.ahora)

                rebanada = Rebanada(
                    n_pasos=n_pasos_h,
                    tiempo=h.tiempo,
                    resultados=símismo.resultados[str(h)],
                    externos=símismo._gen_externos(h, n_pasos_h)
                )
                grupo.start_soon(h.incr, rebanada)

    async def correr_asinc(símismo):
        t_ant = 0
        while q := símismo.quedan:
            t_máximo = max(h.próximo_paso() for h in q)
            próximos = {str(h): h for h in q if h.próximo_paso() == t_máximo}

            await símismo.incr_asinc(n_pasos=t_máximo - t_ant, hilos=próximos)
            t_ant = t_máximo

    async def cerrar_asinc(símismo):
        async with trio.open_nursery() as grupo:
            for h in símismo.hilos.values():
                grupo.start_soon(h.cerrar)

    @property
    def quedan(símismo) -> List[Hilo]:
        return [h for h in símismo.hilos.values() if not h.tiempo.terminado]

    def _gen_externos(símismo, hilo: Hilo, n_pasos: int) -> xr.Dataset:
        tiempo = hilo.tiempo
        f_inic = tiempo.ahora
        f_final = tiempo.eje[tiempo.paso + n_pasos]

        externos: Dict[str, xr.DataArray] = {}
        for req in hilo.requísitos:
            res = símismo.resultados[str(req.hilo)].valores
            externo = res[str(req.var_fuente)][f_inic, f_final]

            remuestreo = req.transf(externo).resample(indexer={EJE_TIEMPO: tiempo.unids.unid_retallo})
            externos[str(req.var_recep)] = getattr(remuestreo, req.integ_tiempo)()

        return xr.Dataset(externos)
