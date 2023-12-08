import os
from typing import Optional, Type

import xarray as xr

from fnt.tinamit3.modelo import Modelo, SimulModelo
from fnt.tinamit3 import Rebanada
from fnt.tinamit3.tiempo import Tiempo
from fnt.tinamit3 import EJE_TIEMPO
from .funcs import gen_mod_pysd, gen_vars_pysd, obt_unid_t_mod_pysd


class ModeloPySD(Modelo):
    def __init__(símismo, archivo: str, nombre: Optional[str] = None):
        símismo.archivo = archivo

        mod = gen_mod_pysd(archivo)
        unid_tiempo = obt_unid_t_mod_pysd(mod)

        nombre = nombre or os.path.splitext(os.path.split(archivo)[1])[0]
        super().__init__(nombre, variables=gen_vars_pysd(mod), unid_tiempo=unid_tiempo)

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulPySD


class SimulPySD(SimulModelo):

    def __init__(símismo, modelo: ModeloPySD, tiempo: Tiempo):
        símismo._inst_pysd = gen_mod_pysd(modelo.archivo)
        símismo.t_inic = símismo._inst_pysd.components.initial_time()

        super().__init__(modelo, tiempo)

    async def incr(símismo, rebanada: Rebanada):
        inic = símismo.t_inic + símismo.tiempo.paso
        tiempos = range(inic + 1, inic + rebanada.n_pasos + 1)

        externos = rebanada.externos.to_dataframe() if rebanada.externos else None

        egr = símismo._inst_pysd.run(
            params=externos,
            initial_condition='current',
            return_columns=['TIME', [vr.nombre_pysd for vr in rebanada.variables]],
            return_timestamps=tiempos
        ).rename(columns={'TIME': EJE_TIEMPO})

        egr[EJE_TIEMPO] = rebanada.eje
        egr = egr.set_index(EJE_TIEMPO)

        await rebanada.recibir(xr.Dataset.from_dataframe(egr))

        await super().incr(rebanada)
