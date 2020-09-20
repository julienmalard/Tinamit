from subprocess import Popen
from typing import Type, List, Optional, Dict

import xarray as xr

from ..idm.puertos_async import IDMEnchufesAsinc
from ..modelo import SimulModelo, Modelo
from ..rebanada import Rebanada
from ..tiempo import Tiempo


class ModeloIDM(Modelo):

    @property
    def simulador(símismo) -> Type[SimulModelo]:
        return SimulIDM


class SimulIDM(SimulModelo):

    def __init__(
            símismo,
            modelo: ModeloIDM,
            tiempo: Tiempo,
            comanda: List,
            args_proceso: Optional[Dict] = None
    ):
        super().__init__(modelo, tiempo)
        símismo.comanda = comanda
        símismo.idm = IDMEnchufesAsinc()
        símismo.proceso = Popen(comanda, **args_proceso)

    async def iniciar(símismo):
        await símismo.idm.activar()

    async def incr(símismo, rebanada: Rebanada):
        for paso in rebanada:
            for var in paso.externos:
                await símismo.idm.cambiar(var, paso.externos[var])

            await símismo.idm.incrementar(paso.n_pasos)

            egr = {var: await símismo.idm.recibir(var) for var in paso.quiere}
            paso.recibir(xr.Dataset.from_dataframe(egr))

    async def cerrar(símismo):
        await símismo.idm.cerrar()
        símismo.proceso.terminate()
