from subprocess import Popen
from typing import List, Optional, Dict

import xarray as xr

from utils import EJE_TIEMPO
from ..idm.puertos_asinc import IDMEnchufesAsinc
from ..modelo import SimulModelo, Modelo
from ..rebanada import Rebanada
from ..tiempo import Tiempo


class SimulIDM(SimulModelo):

    def __init__(
            símismo,
            modelo: Modelo,
            tiempo: Tiempo,
            comanda: List,
            args_proceso: Optional[Dict] = None
    ):
        super().__init__(modelo, tiempo)
        símismo.comanda = comanda
        símismo.args_proceso = args_proceso

        símismo.idm = IDMEnchufesAsinc()
        símismo.proceso: Optional[Popen] = None

    async def iniciar(símismo, rebanada: Rebanada):
        await símismo.idm.conectar()
        puerto = símismo.idm.puerto
        símismo.proceso = Popen(símismo.comanda + ['-p', str(puerto)], **símismo.args_proceso)
        await símismo.idm.activar()

        rebanada.recibir(xr.Dataset(
            {
                str(var): ([EJE_TIEMPO], await símismo.idm.recibir(str(var))) for var in rebanada.variables
            }, coords={EJE_TIEMPO: rebanada.eje}
        ))

    async def incr(símismo, rebanada: Rebanada):
        for paso in rebanada:
            for var in paso.externos:
                await símismo.idm.cambiar(var, paso.externos[var])

            await símismo.idm.incrementar(1)

            egr = {var: await símismo.idm.recibir(str(var)) for var in paso.rebanada.variables}
            paso.recibir(xr.Dataset.from_dict(egr))

        await super().incr(rebanada)

    async def cerrar(símismo):
        await símismo.idm.cerrar()
        símismo.proceso.terminate()
