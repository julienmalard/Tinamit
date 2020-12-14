import os
import unittest
from typing import List

import numpy as np
import pandas as pd
import xarray as xr
import xarray.testing as xrt

from tinamit.conectado import Conectado
from tinamit.conex import ConexiónVars, ConexiónVarsContemporánea
from tinamit.modelo import Modelo, SimulModelo
from tinamit.rebanada import Rebanada
from tinamit.tiempo import UnidTiempo, EspecTiempo
from tinamit.utils import EJE_TIEMPO
from tinamit.variables import Variable

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/bf/prueba_bf.py')
arch_mds = os.path.join(dir_act, 'recursos/mds/prueba_senc_mdl.mdl')


class PruebaConectado(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        class SimulMiModelo(SimulModelo):

            async def iniciar(símismo, rebanada: Rebanada):
                rebanada.recibir(xr.Dataset(
                    {str(vr): (EJE_TIEMPO, [0]) for vr in rebanada.variables},
                    coords={EJE_TIEMPO: [símismo.tiempo.ahora]})
                )

            async def incr(símismo, rebanada: Rebanada):
                vals = np.arange(símismo.tiempo.paso + 1, símismo.tiempo.paso + rebanada.n_pasos + 1)
                datos_egr = {str(vr): ([EJE_TIEMPO], vals) for vr in rebanada.variables if vr.egreso}
                datos_ingr = {
                    str(vr): (
                        [EJE_TIEMPO], rebanada.externos[str(vr)]
                        if str(vr) in rebanada.externos else np.full(rebanada.n_pasos, 0)
                    )
                    for vr in rebanada.variables if vr.ingreso
                }
                datos = {**datos_egr, **datos_ingr}

                coords = {EJE_TIEMPO: rebanada.eje}
                rebanada.recibir(xr.Dataset(datos, coords))
                await super().incr(rebanada)

        class MiModelo(Modelo):
            hilo = SimulMiModelo

            def __init__(símismo, nombre: str, variables: List[Variable] = None, unid_tiempo="día"):
                variables = variables or [
                    Variable("i", ingreso=True, egreso=False, modelo=nombre, unids="m"),
                    Variable("e", ingreso=False, egreso=True, modelo=nombre, unids="m")
                ]
                d_variables = {
                    str(v): v for v in variables
                }
                super().__init__(nombre, d_variables, unid_tiempo=unid_tiempo)

        cls.clase_modelo = MiModelo

    def test_unidireccional(símismo):
        mod1 = símismo.clase_modelo('mod1')
        mod2 = símismo.clase_modelo('mod2')
        conectado = Conectado(
            'conectado', modelos=[mod1, mod2],
            conex=[ConexiónVars("e", "i", mod1, mod2)]
        )
        f_inic = '2000-01-01'
        res = conectado.simular(EspecTiempo(10, f_inic=f_inic))
        res_mod1 = res['mod1'].valores
        res_mod2 = res['mod2'].valores

        eje_t = pd.date_range(f_inic, periods=11, freq='D')
        ref_i = np.roll(np.arange(11.), 1)
        ref_i[0] = 0

        ref_mod1 = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(11.)), 'i': ([EJE_TIEMPO], np.full(11, 0))},
            coords={EJE_TIEMPO: eje_t}
        )
        ref_mod2 = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(11.)), 'i': ([EJE_TIEMPO], ref_i)},
            coords={EJE_TIEMPO: eje_t}
        )

        xrt.assert_equal(res_mod1, ref_mod1)
        xrt.assert_equal(res_mod2, ref_mod2)

    def test_bidireccional(símismo):
        mod1 = símismo.clase_modelo('mod1')
        mod2 = símismo.clase_modelo('mod2')
        conectado = Conectado(
            'conectado',
            modelos=[mod1, mod2],
            conex=[
                ConexiónVarsContemporánea("e", "i", mod1, mod2),
                ConexiónVars("e", "i", mod2, mod1)
            ]
        )
        f_inic = '2000-01-01'
        res = conectado.simular(EspecTiempo(10, f_inic=f_inic))

        ref_i = np.roll(np.arange(11.), 1)
        ref_i[0] = 0

        eje_t = pd.date_range(f_inic, periods=11, freq='D')
        ref_1 = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(11.)), 'i': ([EJE_TIEMPO], ref_i)},
            coords={EJE_TIEMPO: eje_t}
        )

        ref_2 = xr.Dataset(
            {vr: ([EJE_TIEMPO], np.arange(11.)) for vr in ['i', 'e']},
            coords={EJE_TIEMPO: eje_t}
        )

        xrt.assert_equal(res['mod1'].valores, ref_1)
        xrt.assert_equal(res['mod2'].valores, ref_2)

    def test_unid_tiempos_distintos(símismo):
        mod_día = símismo.clase_modelo('día', unid_tiempo='día')
        mod_mes = símismo.clase_modelo('mes', unid_tiempo='mes')

        conectado = Conectado(
            'conectado',
            modelos=[mod_día, mod_mes],
            conex=[
                ConexiónVars("e", "i", mod_día, mod_mes),
                ConexiónVars("e", "i", mod_mes, mod_día)
            ]
        )
        f_inic = '2000-01-01'
        res = conectado.simular(EspecTiempo(12, f_inic=f_inic))

        d_por_m = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        ref_i_día = np.zeros(367)
        ref_i_día[1:] = np.repeat(np.arange(12), d_por_m)
        ref_día = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(367.)), 'i': ([EJE_TIEMPO], ref_i_día)},
            coords={EJE_TIEMPO: pd.date_range(f_inic, periods=367, freq='D')}
        )

        ref_i_mes = np.zeros(13)
        ref_i_mes[2:] = np.cumsum(d_por_m[:-1])
        ref_mes = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(13.)), 'i': ([EJE_TIEMPO], ref_i_mes)},
            coords={EJE_TIEMPO: pd.date_range(f_inic, periods=13, freq='MS')}
        )

        xrt.assert_equal(res['día'].valores, ref_día)
        xrt.assert_equal(res['mes'].valores, ref_mes)

    def test_unid_tiempo_usuario(símismo):
        mod_mes = símismo.clase_modelo('mes', unid_tiempo='mes')
        mod_estacional = símismo.clase_modelo('estación', unid_tiempo=UnidTiempo('mes', n=3))

        conectado = Conectado(
            'conectado', [mod_mes, mod_estacional], conex=[
                ConexiónVars("e", "i", mod_estacional, mod_mes),
                ConexiónVars("e", "i", mod_mes, mod_estacional)
            ]
        )

        f_inic = '2000-01-01'
        res = conectado.simular(EspecTiempo(5, f_inic=f_inic))

        ref_i_mes = np.zeros(5 * 3 + 1)
        ref_i_mes[1:] = np.repeat(np.arange(5),3)
        ref_mes = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(16)), 'i': ([EJE_TIEMPO], ref_i_mes)},
            coords={EJE_TIEMPO: pd.date_range(f_inic, periods=16, freq='MS')}
        )
        ref_i_est = np.zeros(5 + 1)
        ref_i_est[1:] = np.arange(5) * 3
        ref_estacional = xr.Dataset(
            {'e': ([EJE_TIEMPO], np.arange(6)), 'i': ([EJE_TIEMPO], ref_i_est)},
            coords={EJE_TIEMPO: pd.date_range(f_inic, periods=6, freq='3MS')}
        )

        xrt.assert_equal(res['mes'].valores, ref_mes)
        xrt.assert_equal(res['estación'].valores, ref_estacional)

    def test_unid_tiempo_aprox(símismo):
        mod_sem = símismo.clase_modelo('semanal', unid_tiempo='semana')
        mod_mes = símismo.clase_modelo('mensual', unid_tiempo='mes')

        conectado = Conectado(
            'conectado', [mod_sem, mod_mes], conex=[
                ConexiónVars("e", "i", mod_sem, mod_mes),
                ConexiónVars("e", "i", mod_mes, mod_sem)
            ]
        )
        res = conectado.simular(EspecTiempo(11, f_inic='2000-01-01'))
        raise NotImplementedError

    def test_3_horizontal(símismo):
        mod1 = símismo.clase_modelo('mod1')
        mod2 = símismo.clase_modelo('mod2')
        mod3 = símismo.clase_modelo('mod3')

        conectado = Conectado(
            'conectado',
            modelos=[mod1, mod2, mod3],
            conex=[
                ConexiónVars("e", "i", mod1, mod2),
                ConexiónVars("i", "i", mod2, mod3),
                ConexiónVars("i", "i", mod3, mod1)
            ]
        )
        res = conectado.simular(10)

        xrt.assert_equal(res['mod1'].valores, ref_mod1)
        xrt.assert_equal(res['mod2'].valores, ref_mod2)
        xrt.assert_equal(res['mod3'].valores, ref_mod3)

    def test_3_jerárquico(símismo):
        mod1 = símismo.clase_modelo('mod1')
        mod2 = símismo.clase_modelo('mod2')
        mod3 = símismo.clase_modelo('mod3')

        subconectado = Conectado(
            'subconectado',
            modelos=[mod1, mod2],
            conex=[
                ConexiónVars("e", "i", mod1, mod2)
            ]
        )
        conectado = Conectado(
            'subconectado',
            modelos=[subconectado, mod3],
            conex=[
                ConexiónVars("mod2.i", "i", subconectado, mod3),
                ConexiónVars("i", "mod1.i", mod3, subconectado),
            ]
        )
        res = conectado.simular(10)

        xrt.assert_equal(res['mod1'].valores, ref_mod1)
        xrt.assert_equal(res['mod2'].valores, ref_mod2)
        xrt.assert_equal(res['mod3'].valores, ref_mod3)


class PruebaTranformadores(unittest.TestCase):
    def test_agregar_tiempo(símismo):
        raise NotImplementedError

    def test_agregar_eje(símismo):
        raise NotImplementedError

    def test_renombrar_eje(símismo):
        raise NotImplementedError

    def test_función_usuario(símismo):
        raise NotImplementedError

    def test_factor_conv(símismo):
        raise NotImplementedError

    def test_conv_unids_auto(símismo):
        raise NotImplementedError
