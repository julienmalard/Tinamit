import os
from typing import Optional

import xarray as xr

from tinamit3.modelo import Modelo, SimulModelo
from tinamit3.rebanada import Rebanada
from tinamit3.tiempo import Tiempo
from .funcs import gen_mod_pysd, gen_vars_pysd


class ModeloPySD(Modelo):
    def __init__(símismo, archivo: str, nombre: Optional[str] = None):
        símismo.archivo = archivo
        nombre = nombre or os.path.splitext(os.path.split(archivo)[1])[0]
        super().__init__(nombre, variables=gen_vars_pysd(archivo))

    def simulador(símismo):
        return SimulPySD


class SimulPySD(SimulModelo):

    def __init__(símismo, modelo: ModeloPySD, tiempo: Tiempo):
        símismo._inst_pysd = gen_mod_pysd(modelo.archivo)

        super().__init__(modelo, tiempo)

    async def incr(símismo, rebanada: Rebanada):
        egr = símismo._inst_pysd.run(
            params=rebanada.externos,
            initial_condition='current',
            return_columns=[vr.nombre_pysd for vr in rebanada.variables],
            return_timestamps=rebanada.eje
        )
        rebanada.recibir(xr.Dataset.from_dataframe(egr))
