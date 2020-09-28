import shutil
import tempfile
from typing import Type, Optional

from rebanada import Rebanada
from tinamit.envolt.enchufes import SimulIDM
from tinamit.modelo import Modelo, SimulModelo
from tinamit.tiempo import Tiempo


class ModeloSWATPlus(Modelo):
    descargas = 'https://github.com/joelz575/swatplus'

    def __init__(
            símismo,
            archivo: str,
            nombre: str = "SWAT+",
            exe_SAHYSMOD: Optional[str] = None
    ):
        símismo.archivo = archivo
        símismo.exe_SAHYSMOD = exe_SAHYSMOD

        super().__init__(nombre, variables, unid_tiempo='día')

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulSWATPlus


class SimulSWATPlus(SimulIDM):

    def __init__(
            símismo,
            modelo: ModeloSWATPlus,
            tiempo: Tiempo
    ):
        símismo.direc_trabajo = tempfile.mkdtemp()

        comanda = [símismo.exe_SWATPlus]
        args_proceso = {"cwd": símismo.direc_trabajo}
        super().__init__(modelo, tiempo, comanda, args_proceso)

    async def cerrar(símismo):
        await super().cerrar()
        shutil.rmtree(símismo.direc_trabajo)
