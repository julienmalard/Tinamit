import os
import shutil
import tempfile
from copy import deepcopy
from numbers import Number
from typing import Type, Optional

import numpy as np
import trio
import xarray as xr

from fnt.tinamit3.instalador import obt_exe
from fnt.tinamit3.modelo import Modelo, SimulModelo
from fnt.tinamit3 import Rebanada
from fnt.tinamit3.tiempo import Tiempo
from ._arch_egr import leer_arch_egr
from ._arch_ingr.ie import leer_info_dic_paráms, escribir_desde_dic_paráms
from ._vars import gen_variables_sahysmod


class ModeloSAHYSMOD(Modelo):
    descargas = 'https://github.com/julienmalard/sahysmod-sourcecode'

    def __init__(
            símismo,
            archivo: str,
            nombre: str = "SAHYSMOD",
            exe_SAHYSMOD: Optional[str, Number] = None
    ):
        símismo.archivo = archivo
        símismo.dic_paráms = leer_info_dic_paráms(archivo)
        símismo.exe_SAHYSMOD = obt_exe('SAHYSMOD', símismo.descargas, exe_SAHYSMOD)

        variables = gen_variables_sahysmod(símismo.dic_paráms)
        super().__init__(nombre, variables, unid_tiempo='mes')

        # Establecer los variables climáticos.
        símismo.conectar_clima(var='Pp - Rainfall', var_clima='بارش', transf=0.001, integ_tiempo='sum')

    @property
    def hilo(símismo) -> Type[SimulModelo]:
        return SimulSAHYSMOD


class SimulSAHYSMOD(SimulModelo):

    def __init__(símismo, modelo: ModeloSAHYSMOD, tiempo: Tiempo):
        símismo.direc_trabajo = tempfile.mkdtemp()
        símismo.arch_egreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')
        símismo.arch_ingreso = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.inp')
        símismo.comanda = [modelo.exe_SAHYSMOD, símismo.arch_ingreso, símismo.arch_egreso]

        símismo.dic_paráms = deepcopy(modelo.dic_paráms)

        super().__init__(modelo, tiempo)

    async def avanzar_modelo(símismo, n_ciclos: int):

        símismo._verificar_estado_vars()

        await símismo._escribir_archivo_ingr(n_ciclos=n_ciclos, archivo=arch_ingreso)

        # Limpiar archivos de egresos que podrían estar allí
        if os.path.isfile(símismo.arch_egreso):
            os.remove(símismo.arch_egreso)

        # Correr la comanda desde la línea de comanda
        await trio.run_process(símismo.comanda, cwd=símismo.direc_trabajo)

        # Verificar que SAHYSMOD generó egresos.
        if not os.path.isfile(símismo.arch_egreso):
            async with await trio.open_file(os.path.join(símismo.direc_trabajo, 'error.lst')) as d:
                mnsj_sahysmod = d.readlines()

            raise FileNotFoundError(
                '\n\nEl modelo SAHYSMOD no generó egreso. Esto probablemente quiere decir que tuvo problema interno.'
                '\n\t¡Diviértete! :)'
                '\nEl archivo de ingresos está en: {arch}'
                '\nMensajes de error de SAHYSMOD:'
                '\n{mnsj}'.format(arch=símismo.arch_ingreso, mnsj=mnsj_sahysmod))

        await símismo._leer_egr_modelo(n_ciclos=n_ciclos)

    async def incr(símismo, rebanada: Rebanada):

        return await super().incr(rebanada)

    async def _escribir_archivo_ingr(símismo, n_ciclos: int, archivo: str):
        # Establecer el número de años de simulación
        símismo.dic_paráms['NY'] = n_ciclos

        # Copiar datos desde el diccionario de ingresos
        for var in símismo.variables.egresos():
            llave = var.cód.replace('#', '').upper()
            if llave in símismo.dic_paráms:
                m = símismo.dic_paráms[llave]

                if isinstance(var, VarBloqSAHYSMOD):
                    val = var.obt_vals_paso()
                    if m.shape == val.shape:
                        m[:] = val
                    else:
                        m[:] = val[-1]
                else:
                    val = var.obt_val()
                    m[:] = val
                m[np.isnan(m)] = -1

        # Y finalmente, escribir el fuente de valores de ingreso
        await escribir_desde_dic_paráms(dic_paráms=símismo.dic_paráms, archivo_obj=archivo)

    def _verificar_estado_vars(símismo) -> None:
        # Aquí tenemos que verificar el estado interno de SAHYSMOD porque éste, siendo SAHYSMOD, da mensajes de error
        # con el mínimo de información posible.

        a = símismo.variables['Area A - Seasonal fraction area crop A'].obt_vals_paso()
        b = símismo.variables['Area B - Seasonal fraction area crop B'].obt_vals_paso()
        fsa = símismo.variables['FsA - Water storage efficiency crop A'].obt_vals_paso()
        fsb = símismo.variables['FsB - Water storage efficiency crop B'].obt_vals_paso()

        if np.any(np.logical_and(fsa == -1, a > 0)):
            raise ValueError('Los valores de FsA no pueden faltar en polígonos que tienen superficie con cultivo A.')

        if np.any(np.logical_and(fsb == -1, b > 0)):
            raise ValueError('Los valores de FsB no pueden faltar en polígonos que tienen superficie con cultivo B.')

    async def _leer_egr_modelo(símismo, n_ciclos: int) -> xr.Dataset:
        archivo = os.path.join(símismo.direc_trabajo, 'SAHYSMOD.out')

        dic_egr = await leer_arch_egr(
            archivo=archivo, años=n_ciclos
        )

        # Convertir códigos de variables a nombres de variables
        for c, v in dic_egr.items():
            try:
                símismo.variables.cód_a_var(c).poner_vals_paso(v[0])  # v[0] para quitar dimensión de año
            except KeyError:
                pass

        return xr.Dataset({
            vr: xr.DataArray.from_dict(vl) for vr, vl in dic_egr.items()
        })

    async def cerrar(símismo):
        shutil.rmtree(símismo.direc_trabajo)
