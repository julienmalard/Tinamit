import os
import shutil
import tempfile
from typing import List, Type

from tinamit3.envolt.enchufes import SimulIDM
from tinamit3.modelo import Modelo, SimulModelo
from tinamit3.tiempo import Tiempo
from ._ie import escribir_desde_dic_paráms
from ._vars import gen_variables_SAHYSMOD


class ModeloSAHYSMODIDM(Modelo):

    def __init__(símismo, archivo, nombre: str = "SAHYSMOD"):
        símismo.archivo = archivo
        variables = gen_variables_SAHYSMOD(archivo)

        super().__init__(nombre, variables, unid_tiempo='mes')

    @property
    def simulador(símismo) -> Type[SimulModelo]:
        return SimulSAHYSMODIDM


class SimulSAHYSMODIDM(SimulIDM):

    def __init__(
            símismo,
            modelo: Modelo,
            tiempo: Tiempo,
            comanda: List
    ):
        símismo.direc_trabajo = tempfile.mkdtemp()
        args_proceso = {"cwd": símismo.direc_trabajo}

        super().__init__(modelo, tiempo, comanda, args_proceso)

    async def iniciar(símismo):
        arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')

        await escribir_desde_dic_paráms(dic_paráms, archivo_obj=arch_ingreso)
        return await super().iniciar()

    async def cerrar(símismo):
        await super().cerrar()
        shutil.rmtree(símismo.direc_trabajo)
