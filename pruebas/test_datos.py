import datetime as ft
import os
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import tinamit.datos.fuente as fnt
import xarray as xr
import xarray.testing as xrt
from tinamit.config import _
from tinamit.datos.bd import BD

dir_act = os.path.split(__file__)[0]
arch_datos1 = os.path.join(dir_act, 'recursos/datos/datos.csv')
arch_datos2 = os.path.join(dir_act, 'recursos/datos/datos2.csv')


class TestGeneraFuentes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dic_datos = {
            'lugar': [708, 708, 7],
            'fecha': ['2000', '2002', '2000'],
            'var_completo': [1, 2, 2],
            'var_incompleto': [np.nan, 10, 20],
            'temp': [1, 1, 1]
        }

        cls.bds = {
            'pandas': fnt.FuentePandas(pd.DataFrame(dic_datos), 'Pandas'),
            'csv': fnt.FuenteCSV(arch_datos1, 'CSV'),
            'dic': fnt.FuenteDic(dic_datos, 'Dic'),
            'xarray': fnt.FuenteBaseXarray(xr.Dataset(
                {
                    'var_completo': ('n', dic_datos['var_completo']),
                    'var_incompleto': ('n', dic_datos['var_incompleto']),
                    'fecha': ('n', dic_datos['fecha']),
                    'lugar': ('n', dic_datos['lugar'])
                }
            ), 'Xarray', fechas='fecha', lugares='lugar'
            )
        }

    def test_obt_datos(símismo):
        for nmb, bd in símismo.bds.items():
            with símismo.subTest(bd=nmb):
                datos = bd.obt_vals(['var_completo'])
                npt.assert_array_equal(datos['var_completo'], [1, 2, 2])

    def test_obt_datos_faltan(símismo):
        for nmb, bd in símismo.bds.items():
            with símismo.subTest(bd=nmb):
                datos = bd.obt_vals(['var_incompleto'])
                npt.assert_array_equal(datos['var_incompleto'], [np.nan, 10, 20])


class TestFuentes(unittest.TestCase):

    def test_fechas_columna(símismo):
        fechas = ['1947-8-14', '1947-8-15']
        fuente = fnt.FuentePandas(pd.DataFrame({'a': [1, 2], 'f': fechas}), 'prueba', fechas='f')
        lista_fechas_igual(fuente.obt_vals('a')[_('fecha')].values, fechas)

    def test_fechas_texto_año(símismo):
        fuente = fnt.FuentePandas(pd.DataFrame({'a': [1, 2]}), 'prueba', fechas='1966')
        lista_fechas_igual(fuente.obt_vals('a')[_('fecha')].values, [ft.date(1966, 1, 1)] * 2)

    def test_fechas_ft(símismo):
        fecha = ft.date(1966, 1, 1)
        fuente = fnt.FuentePandas(pd.DataFrame({'a': [1, 2]}), 'prueba', fechas=fecha)
        lista_fechas_igual(fuente.obt_vals('a')[_('fecha')].values, [fecha] * 2)

    def test_fecha_texto(símismo):
        fecha = '1966-7-21'
        fuente = fnt.FuentePandas(pd.DataFrame({'a': [1, 2]}), 'prueba', fechas=fecha)
        lista_fechas_igual(fuente.obt_vals('a')[_('fecha')].values, [fecha] * 2)

    def test_fechas_error(símismo):
        with símismo.assertRaises(ValueError):
            fnt.FuentePandas(pd.DataFrame({'a': [1, 2]}), 'prueba', fechas='No soy una columna').obt_vals('a')

    def test_lugares_columna(símismo):
        lugar = ['1', '2']
        fuente = fnt.FuentePandas(pd.DataFrame({'a': [1, 2], 'l': lugar}), 'prueba', lugares='l')
        lugares_fuente = fuente.obt_vals('a').lugar.values.tolist()
        símismo.assertListEqual(lugares_fuente, lugar)

    def test_lugares_texto(símismo):
        fuente = fnt.FuentePandas(pd.DataFrame({'a': [1, 2]}), 'prueba', lugares='708')
        lugares_fuente = fuente.obt_vals('a')[_('lugar')].values.tolist()
        símismo.assertEqual(lugares_fuente, ['708', '708'])


class TestBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fnt1 = fnt.FuenteCSV(arch_datos1, nombre='prueba 1', fechas='fecha', lugares='lugar')
        fnt2 = fnt.FuenteCSV(arch_datos2, nombre='prueba 1', fechas='fecha', lugares='lugar')
        cls.bd = BD(fuentes=[fnt1, fnt2])

    def test_obt_datos_1_var(símismo):
        res = símismo.bd.obt_vals('var_completo')
        símismo.assertSetEqual(_a_conj(res, 'lugar'), {'701', '708', '7'})
        símismo.assertEqual(res.name, 'var_completo')

    def test_obt_datos_multi_vars(símismo):
        res = símismo.bd.obt_vals(['var_completo', 'var_incompleto'])
        símismo.assertSetEqual(_a_conj(res, 'lugar'), {'701', '708', '7'})
        símismo.assertIn('var_completo', res)
        símismo.assertIn('var_incompleto', res)

    def test_obt_datos_de_lugar(símismo):
        res = símismo.bd.obt_vals('var_completo', lugares='708')
        símismo.assertTrue(_a_conj(res, 'lugar') == {'708'})

    def test_obt_datos_fecha_única(símismo):
        res = símismo.bd.obt_vals('var_completo', fechas='2000')
        símismo.assertTrue(fechas_en_rango(res[_('fecha')], ['2000-1-1', '2000-12-31']))
        npt.assert_equal(res.values, [1, 2])

    def test_obt_datos_fecha_lista(símismo):
        res = símismo.bd.obt_vals('var_completo', fechas=['2000', '2002'])
        símismo.assertTrue(fechas_en_lista(res[_('fecha')], ['2000-01-01', '2002-01-01']))

    def test_obt_datos_fecha_rango(símismo):
        res = símismo.bd.obt_vals('var_completo', fechas=('2000', '2002-6-1'))
        símismo.assertTrue(fechas_en_rango(res[_('fecha')], ('2000-1-1', '2002-6-1')))

    def test_interpol_no_necesaria(símismo):
        res = símismo.bd.interpolar('var_completo', fechas=('2000', '2002-1-1'), lugares='708')

        ref = símismo.bd.obt_vals('var_completo', lugares='708')
        xrt.assert_equal(
            res.where(res[_('fecha')].isin(pd.to_datetime(('2000', '2002-1-1'))), drop=True),
            ref.where(ref[_('fecha')].isin(pd.to_datetime(('2000', '2002-1-1'))), drop=True)
        )

    def test_interpol_con_fecha_única(símismo):
        res = símismo.bd.interpolar(['var_incompleto', 'var_completo'], fechas='2001')

        # Verificar interpolaciones
        vals = res.where(
            np.logical_and(res[_('lugar')] == '7', res[_('fecha')] == np.datetime64('2001-01-01')),
            drop=True
        )
        npt.assert_allclose(vals['var_completo'].values, 2.500684)
        npt.assert_allclose(vals['var_incompleto'].values, 23.3394, rtol=0.001)

    def test_interpol_con_fecha_rango(símismo):
        l_vars = ['var_incompleto', 'var_completo']
        res = símismo.bd.interpolar(l_vars, fechas=('2000', '2002-6-1'))
        npt.assert_allclose(res['var_incompleto'].sel(lugar='7'), [20, 28.05], rtol=0.01)


def _a_conj(bd, var):
    return set(np.unique(bd[var].values).tolist())


def lista_fechas_igual(l1, l2):
    lista_ls = [l1, l2]
    for i, l in enumerate(lista_ls):
        if not isinstance(l, np.ndarray):
            lista_ls[i] = np.array(pd.to_datetime(l), dtype='datetime64')
        else:
            if not np.issubdtype(l.dtype, np.datetime64):
                lista_ls[i] = l.astype('datetime64')

    npt.assert_array_equal(lista_ls[0], lista_ls[1])


def fechas_en_lista(f, l):
    l = np.array(pd.to_datetime(l), dtype='datetime64')

    return np.all(f.isin(l))


def fechas_en_rango(f, r):
    r = np.array(pd.to_datetime(r), dtype='datetime64')

    return np.all(f <= r[1]) and np.all(f >= r[0])
