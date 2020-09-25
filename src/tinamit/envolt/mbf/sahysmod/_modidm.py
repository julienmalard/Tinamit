import math
import os
import shutil
import tempfile
from copy import deepcopy
from typing import Type, Optional

from fnt.tinamit3 import SimulIDM
from fnt.tinamit3.instalador import obt_exe
from fnt.tinamit3.modelo import Modelo, SimulModelo
from fnt.tinamit3.tiempo import Tiempo
from ._arch_ingr.ie import escribir_desde_dic_paráms, leer_info_dic_paráms
from ._vars import gen_variables_sahysmod


class ModeloSAHYSMODIDM(Modelo):
    descargas = 'https://github.com/julienmalard/sahysmod-sourcecode'

    def __init__(
            símismo,
            archivo: str,
            nombre: str = "SAHYSMOD",
            exe_SAHYSMOD: Optional[str] = None
    ):
        símismo.archivo = archivo
        símismo.dic_paráms = leer_info_dic_paráms(archivo)
        símismo.exe_SAHYSMOD = obt_exe('SAHYSMOD_IDM', símismo.descargas, exe_SAHYSMOD)

        variables = gen_variables_sahysmod(símismo.dic_paráms)

        super().__init__(nombre, variables, unid_tiempo='mes')

        # Establecer los variables climáticos.
        símismo.conectar_clima(var='Pp - Rainfall', var_clima='بارش', transf=0.001, integ_tiempo='sum')

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulSAHYSMODIDM


class SimulSAHYSMODIDM(SimulIDM):

    def __init__(
            símismo,
            modelo: ModeloSAHYSMODIDM,
            tiempo: Tiempo
    ):
        símismo.direc_trabajo = tempfile.mkdtemp()

        arch_egreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')
        arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')
        comanda = [modelo.exe_SAHYSMOD, arch_ingreso, arch_egreso]

        args_proceso = {"cwd": símismo.direc_trabajo}
        super().__init__(modelo, tiempo, comanda, args_proceso)

        # Debe venir después de `super()` para acceder a `símismo.tiempo` ajustado
        símismo.dic_paráms = deepcopy(modelo.dic_paráms)
        símismo.dic_paráms['NY'] = math.ceil(símismo.tiempo.n_pasos / 12)

    async def iniciar(símismo):
        arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')

        await escribir_desde_dic_paráms(símismo.dic_paráms, archivo_obj=arch_ingreso)
        return await super().iniciar()

    async def cerrar(símismo):
        await super().cerrar()
        shutil.rmtree(símismo.direc_trabajo)
