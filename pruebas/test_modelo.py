import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import xarray as xr

from pruebas.recursos.mod.prueba_mod import ModeloPrueba
from tinamit.config import trads
from tinamit.tiempo.tiempo import EspecTiempo
from tinamit.mod import OpsSimulGrupoCombin, OpsSimulGrupo

_ = trads.trad


class TestSimular(unittest.TestCase):
    def test_simular_t_int(símismo):
        mod = ModeloPrueba()
        res = mod.simular(t=10)['Escala']
        npt.assert_equal(res.vals, np.arange(11).reshape((11, 1)))

    def test_simular_t_fecha(símismo):
        mod = ModeloPrueba(unid_tiempo='días')
        res = mod.simular(t=EspecTiempo(10, '2001-01-01'))['Escala']
        pdt.assert_index_equal(
            res.vals.indexes[_('fecha')], pd.date_range('2001-01-01', periods=11), check_names=False
        )

    def test_paso(símismo):
        mod = ModeloPrueba()
        res = mod.simular(t=EspecTiempo(10, tmñ_paso=2))['Escala']
        npt.assert_equal(res.vals, np.arange(21, step=2).reshape((11, 1)))
        npt.assert_equal(res.vals.indexes[_('fecha')], np.arange(21, step=2))

    def test_paso_inválido(símismo):
        mod = ModeloPrueba()
        with símismo.assertRaises(ValueError):
            mod.simular(EspecTiempo(100, tmñ_paso=0))

    def test_guardar_cada(símismo):
        mod = ModeloPrueba()
        res = mod.simular(t=EspecTiempo(10, guardar_cada=2))['Escala']
        npt.assert_equal(res.vals, np.arange(11, step=2).reshape((6, 1)))
        npt.assert_equal(res.t.eje(), np.arange(11, step=2))

    def test_guardar_cada_con_fecha(símismo):
        mod = ModeloPrueba(unid_tiempo='días')
        res = mod.simular(t=EspecTiempo(10, '2001-01-01', guardar_cada=2))['Escala']
        npt.assert_equal(res.vals, np.arange(11, step=2).reshape((6, 1)))
        pdt.assert_index_equal(
            res.vals.indexes[_('fecha')], pd.date_range('2001-01-01', periods=6, freq='2D'), check_names=False
        )


class TestSimularGrupo(unittest.TestCase):

    def test_simular_grupo(símismo):
        vals_extern = [{'Escala': 1}, {'Escala': 2}]
        mod = ModeloPrueba()
        ops = OpsSimulGrupo(5, extern=vals_extern)
        res = mod.simular_grupo(ops)
        for corr, vl in zip(res.values(), vals_extern):
            símismo.assertEqual(corr['Escala'].vals.values[0], vl['Escala'])

    def test_simular_grupo_combin(símismo):
        mod = ModeloPrueba()
        ops = OpsSimulGrupoCombin([5, 6], extern=[{'Escala': 1}, {'Escala': 2}])
        res = mod.simular_grupo(ops)
        símismo.assertEqual(len(res), 4)

    def test_simular_grupo_tmñ_erróneo(símismo):
        with símismo.assertRaises(ValueError):
            OpsSimulGrupo([5, 6, 7], extern=[{'Escala': 1}, {'Escala': 2}])

    def test_simular_paralelo(símismo):
        mod = ModeloPrueba()
        ops = OpsSimulGrupoCombin(5, extern=[{'Escala': 1}, {'Escala': 2}])
        sin_paralelo = mod.simular_grupo(ops)
        con_paralelo = mod.simular_grupo(ops, paralelo=True)
        símismo.assertEqual(sin_paralelo, con_paralelo)

    def test_simular_grupo_con_lista_nombres(símismo):
        mod = ModeloPrueba()
        nombres = ['corrida 1', 'corrida 2']
        ops = OpsSimulGrupo(5, extern=[{'Escala': 1}, {'Escala': 2}], nombre=nombres)
        res = mod.simular_grupo(ops)
        símismo.assertSetEqual(set(nombres), set(res))


class TestSimulConDatos(unittest.TestCase):

    @staticmethod
    def _simul_con_extern(extern, ref, var_ref='Vacío', fecha=True):
        f_inic = '2000-01-01' if fecha else None
        res = ModeloPrueba(unid_tiempo='días').simular(t=EspecTiempo(10, f_inic=f_inic), extern=extern)
        npt.assert_equal(res[var_ref].vals.values.reshape(np.array(ref).shape), ref)

    def test_t_fecha_extern_núm(símismo):
        símismo._simul_con_extern({'Vacío': 4}, ref=np.full(11, 4))

    def test_t_fecha_extern_matr(símismo):
        símismo._simul_con_extern({'Vacío2': np.arange(2)}, np.tile(np.arange(2), (11, 1)), var_ref='Vacío2')

    def test_t_fecha_extern_pd_num(símismo):
        extern = pd.DataFrame(data={'Vacío': np.arange(5)}, index=np.arange(10, step=2))
        símismo._simul_con_extern(extern, ref=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4, 4])

    def test_t_fecha_extern_pd_fecha(símismo):
        extern = pd.DataFrame(data={'Vacío': np.arange(4)}, index=pd.date_range('2000-01-02', '2000-01-05'))
        símismo._simul_con_extern(extern, ref=[0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3])

    def test_t_fecha_extern_xr_fecha(símismo):
        extern = {
            'Vacío': xr.DataArray(
                np.arange(11), coords={_('fecha'): pd.date_range('2000-01-01', periods=11)}, dims=[_('fecha')]
            )
        }
        símismo._simul_con_extern(extern, ref=np.arange(11))

    def test_t_fecha_extern_xr_num(símismo):
        extern = {'Vacío': xr.DataArray(np.arange(11), coords={_('fecha'): np.arange(11)}, dims=[_('fecha')])}
        símismo._simul_con_extern(extern, ref=np.arange(11))

    def test_t_fecha_extern_bd_xr(símismo):
        extern = xr.Dataset({'Vacío': (_('fecha'), np.arange(11))}, coords={_('fecha'): np.arange(11)})
        símismo._simul_con_extern(extern, ref=np.arange(11))

    def test_t_numérico(símismo):
        extern = pd.DataFrame(data={'Vacío': np.arange(5)}, index=np.arange(10, step=2))
        símismo._simul_con_extern(extern, fecha=False, ref=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4, 4])

    def test_t_numérico_extern_fecha(símismo):
        extern = pd.DataFrame(data={'Vacío': np.arange(4)}, index=pd.date_range('2000-01-02', '2000-01-05'))
        with símismo.assertRaises(TypeError):
            ModeloPrueba(unid_tiempo='días').simular(t=EspecTiempo(10), extern=extern)
