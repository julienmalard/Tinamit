from datetime import date, datetime
from typing import List
from unittest import TestCase

import numpy as np
import pandas as pd
import xarray as xr
import xarray.testing as xrt

from tinamit.modelo import Modelo
from tinamit.modelo import SimulModelo
from tinamit.rebanada import Rebanada
from tinamit.tiempo import EspecTiempo, UnidTiempo
from tinamit.utils import EJE_TIEMPO
from tinamit.variables import Variable


class PruebaModelo(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        class SimulMiModelo(SimulModelo):

            async def iniciar(símismo, rebanada: Rebanada):
                rebanada.recibir(xr.Dataset(
                    {str(vr): (EJE_TIEMPO, [0]) for vr in rebanada.variables},
                    coords={EJE_TIEMPO: [símismo.tiempo.ahora]})
                )

            async def incr(símismo, rebanada: Rebanada):
                vals = np.arange(símismo.tiempo.paso + 1, símismo.tiempo.paso + rebanada.n_pasos + 1)
                datos = {
                    str(vr): ([EJE_TIEMPO], vals) for vr in rebanada.variables
                }
                coords = {EJE_TIEMPO: rebanada.eje}
                rebanada.recibir(xr.Dataset(datos, coords))
                await super().incr(rebanada)

        class MiModelo(Modelo):
            hilo = SimulMiModelo

            def __init__(símismo, variables: List[Variable] = None, unid_tiempo="día"):
                nombre = "prueba"

                variables = variables or [
                    Variable("a", ingreso=True, egreso=True, modelo=nombre, unids="m"),
                    Variable("b", ingreso=True, egreso=True, modelo=nombre, unids="m")
                ]
                d_variables = {
                    str(v): v for v in variables
                }
                super().__init__(nombre, d_variables, unid_tiempo=unid_tiempo)

        cls.clase_modelo = MiModelo

    def test_simular_t_int(símismo):
        res = símismo.clase_modelo().simular(tiempo=12)['prueba'].valores
        ref = xr.Dataset(
            {str(vr): ([EJE_TIEMPO], np.arange(13)) for vr in ["a", "b"]},
            coords={EJE_TIEMPO: res[EJE_TIEMPO]}
        )
        xrt.assert_equal(res, ref)

    def test_simular_t_fecha(símismo):
        formatos = {
            "str": '1947-08-15',
            "datetime.date": date(1947, 8, 15),
            "datetime.datetime": datetime(1947, 8, 15, 0, 0),
            "pandas.Timestamp": pd.Timestamp(1947, 8, 15)
        }
        ref = xr.Dataset(
            {str(vr): ([EJE_TIEMPO], np.arange(13)) for vr in ["a", "b"]},
            coords={EJE_TIEMPO: pd.date_range('1947-08-15', freq='D', periods=13)}
        )
        for nmb, fmt in formatos.items():
            with símismo.subTest(nmb):
                res = símismo.clase_modelo().simular(tiempo=EspecTiempo(12, f_inic=fmt))['prueba'].valores
                xrt.assert_equal(res, ref)

    def test_unid_tiempo_no_estándar(símismo):
        bisemana = UnidTiempo("día", 14)
        res = símismo.clase_modelo(unid_tiempo=bisemana).simular(12)['prueba'].valores

        ref = xr.Dataset(
            {str(vr): ([EJE_TIEMPO], np.arange(13)) for vr in ["a", "b"]},
            coords={EJE_TIEMPO: res[EJE_TIEMPO]}
        )
        xrt.assert_equal(res, ref)

    def test_simular_variables(símismo):
        res = símismo.clase_modelo().simular(12, variables=["a"])['prueba'].valores

        símismo.assertIn('a', res)
        símismo.assertNotIn('b', res)

        ref = xr.Dataset(
            {str(vr): ([EJE_TIEMPO], np.arange(13)) for vr in ["a"]},
            coords={EJE_TIEMPO: res[EJE_TIEMPO]}
        )
        xrt.assert_equal(res, ref)

    def test_simular_manual(símismo):
        n_pasos = 12
        mod = símismo.clase_modelo()
        simul = mod.iniciar(n_pasos)

        simul.iniciar()
        for _i in range(n_pasos):
            simul.incr(1)
        simul.cerrar()

        res = simul.resultados['prueba'].valores

        ref = xr.Dataset(
            {str(vr): ([EJE_TIEMPO], np.arange(13)) for vr in ["a", "b"]},
            coords={EJE_TIEMPO: res[EJE_TIEMPO]}
        )
        xrt.assert_equal(res, ref)

    def test_variables_multidim(símismo):
        x, y = 10, 5
        n = 12
        variables = [Variable(
            "multidim", unids=None, ingreso=True, egreso=True, coords={'x': np.arange(x), 'y': np.arange(y)},
            dims=['x', 'y'],
            modelo='prueba'
        )]
        res = símismo.clase_modelo(variables=variables).simular(n)['prueba'].valores
        ref = xr.Dataset(
            {"multidim": ([EJE_TIEMPO, 'x', 'y'], np.repeat(np.arange(n + 1), x * y).reshape((n + 1, x, y)))},
            coords={EJE_TIEMPO: res[EJE_TIEMPO], 'x': np.arange(x), 'y': np.arange(y)}
        )
        xrt.assert_equal(res, ref)


"""
externos = Externos({
    'a': 2,
    'b': [1, 2, 3],
    'c': pd.DataFrame([1, 2, 3], index=pd.date_range()),
    'd': pd.DataFrame([1, 2, 3], index=[0, 2, 3]),
    'e': xr.DataArray()
})

mod.simular(10, extras=[externos])
# O...
externos.simular(mod, 10)  # -> Conectado([externos, mod]).simular(10, variables=mod)
(externos + clima).simular(mod, 10)

mod.conectar_clima('Lluvia', 'lluvia')

mod.simular(50, extras=Clima('8.5'))

simul = mod.iniciar(10, extras=externos)
simul.incr(2)
simul.cerrar()
res = simul.resultados()

mod2 = Conectado("conectado", [Modelo1, Modelo2], conex=[
    ConexiónVars('var', 'var', Modelo1, Modelo2, transf=1.5),
    ConexiónVars('var1', 'var2', Modelo1, Modelo2, transf=RenombrarEjes({'eje1': 'eje2'}))
])
mod2.simular(10)

ValsExternos = Externos({
    'a': 2,
    'b': [1, 2, 3],
    'c': pd.DataFrame([1, 2, 3], index=pd.date_range()),
    'd': xr.DataArray()
})
mod = Conectado("otro conectado", [Modelo1])
mod.simular(10, extras=[ValsExternos])

Geografía().simular(mod)

GrupoCombinador([ValsExternos], [Clima(x) for x in {'0', '2.6', '4.5', '6.0', '8.5'}]).simular(mod, 100)

"""
