import datetime as ft
import os
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import xarray as xr

from tinamit.Análisis.Datos import MicroDatos, Datos, SuperBD, obt_fecha_ft

dir_act = os.path.split(__file__)[0]
arch_reg = os.path.join(dir_act, 'recursos/datos/datos.csv')
arch_microdatos = os.path.join(dir_act, 'recursos/datos/microdatos.csv')


class Test_GenerarDatos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dic_datos = {
            'lugar': [708, 708, 7, 7, 7, 701],
            'fecha': ['2000', '2002', '2000', '2002', '2003', '1990'],
            'var_completo': [1, 2, 2, 3, 4, 0],
            'var_incompleto': ['', 10, 20, '', 30, 15],
            'temp': [1, 1, 1, 1, 1, 1]
        }

        cls.bds = {
            'pandas': MicroDatos(
                'Pandas', pd.DataFrame(dic_datos)
            ),
            'csv': MicroDatos('CSV', arch_microdatos),
            'dic': MicroDatos('Dic', dic_datos),
            'dic_anidado': MicroDatos('Dic Anidado', {
                '708': {'fecha': ['2000', '2002'], 'var_completo': [1, 2], 'var_incompleto': ['', 10], 'temp': [1, 1]},
                '7': {'fecha': ['2000', '2002', '2003'], 'var_completo': [2, 3, 4], 'var_incompleto': [20, '', 30],
                      'temp': [1, 1, 1]},
                '701': {'fecha': ['1990'], 'var_completo': [0], 'var_incompleto': [15], 'temp': [1]}
            }),
            'xarray': MicroDatos('Xarray', xr.Dataset(
                {
                    'var_completo': ('n', dic_datos['var_completo']),
                    'var_incompleto': ('n', dic_datos['var_incompleto']),
                    'fecha': ('n', dic_datos['fecha']),
                    'lugar': ('n', dic_datos['lugar'])
                }
            ), tiempo='fecha', lugar='lugar')
        }

    def test_obt_datos(símismo):
        for nmb, bd in símismo.bds.items():
            with símismo.subTest(bd=nmb):
                datos = bd.obt_datos(['var_completo'])
                npt.assert_array_equal(datos['var_completo'], [1, 2, 2, 3, 4, 0])

    def test_obt_datos_faltan(símismo):
        for nmb, bd in símismo.bds.items():
            with símismo.subTest(bd=nmb):
                datos = bd.obt_datos(['var_incompleto'])
                npt.assert_array_equal(datos['var_incompleto'], [np.nan, 10, 20, np.nan, 30, 15])


class TestDatos(unittest.TestCase):

    def test_obt_datos_código_vacío(símismo):
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2, 'jaja']}), cód_vacío='jaja')
        npt.assert_array_equal(bd.obt_datos('a')['a'], [1, 2, np.nan])

    def test_fechas_columna(símismo):
        fechas = ['1947-8-14', '1947-8-15']
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2], 'f': fechas}), tiempo='f')
        lista_fechas_igual(bd.obt_datos('a')['tiempo'].values, fechas)

    def test_fechas_texto_año(símismo):
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2]}), tiempo='1966')
        lista_fechas_igual(bd.obt_datos('a')['tiempo'].values, [ft.date(1966, 1, 1)] * 2)

    def test_fechas_ft(símismo):
        fecha = ft.date(1966, 1, 1)
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2]}), tiempo=fecha)
        lista_fechas_igual(bd.obt_datos('a')['tiempo'].values, [fecha] * 2)

    def test_fecha_texto(símismo):
        fecha = '1966-7-21'
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2]}), tiempo=fecha)
        lista_fechas_igual(bd.obt_datos('a')['tiempo'].values, [fecha] * 2)

    def test_fechas_error(símismo):
        with símismo.assertRaises(ValueError):
            MicroDatos('pueba', pd.DataFrame({'a': [1, 2]}), tiempo='No soy una columna')

    def test_lugares_columna(símismo):
        lugar = ['1', '2']
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2], 'l': lugar}), lugar='l')
        lugares_bd = bd.obt_datos('a').lugar.values.tolist()
        símismo.assertListEqual(lugares_bd, lugar)

    def test_lugares_texto(símismo):
        bd = MicroDatos('prueba', pd.DataFrame({'a': [1, 2]}), lugar='708')
        lugares_bd = bd.obt_datos('a').lugar.values.tolist()
        símismo.assertListEqual(lugares_bd, ['708'] * 2)


class Test_SuperBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bd_región = Datos(nombre='prueba regional', fuente=arch_reg, tiempo='fecha', lugar='lugar')
        bd_indiv = MicroDatos(nombre='prueba individual', fuente=arch_microdatos, tiempo='fecha', lugar='lugar')
        cls.bd = SuperBD(nombre='BD Central', bds=[bd_región, bd_indiv], auto_conectar=True)

        cls.bd.espec_var(var='completo', var_bd='var_completo')
        cls.bd.espec_var(var='incompleto', var_bd='var_incompleto')

    def test_espec_borrar_var(símismo):
        símismo.bd.espec_var(var='var para borrar', var_bd='temp')
        símismo.assertIn('var para borrar', símismo.bd.variables)
        símismo.bd.borrar_var(var='var para borrar')
        símismo.assertNotIn('var para borrar', símismo.bd.variables)

    def test_renombrar_var(símismo):
        símismo.bd.renombrar_var('completo', nuevo_nombre='var renombrado')
        símismo.assertIn('var renombrado', símismo.bd.variables)
        símismo.assertNotIn('completo', símismo.bd.variables)
        símismo.bd.renombrar_var('var renombrado', nuevo_nombre='completo')

    def test_desconectar_datos(símismo):
        bd_temp = MicroDatos(nombre='temp', fuente=arch_microdatos, tiempo='fecha', lugar='lugar')
        símismo.bd.conectar_datos(bd=bd_temp)
        símismo.bd.desconectar_datos(bd=bd_temp)
        símismo.assertNotIn(bd_temp.nombre, símismo.bd.bds)

    def test_guardar_cargar_datos(símismo):
        símismo.bd.guardar_datos()
        datos = símismo.bd.datos.copy()
        microdatos = símismo.bd.microdatos.copy()
        datos_err = símismo.bd.datos_err.copy()
        bd = SuperBD(símismo.bd.nombre)
        bd.cargar_datos()

        símismo.assertTrue(datos.identical(símismo.bd.datos))
        símismo.assertTrue(microdatos.identical(símismo.bd.microdatos))
        símismo.assertTrue(datos_err.identical(símismo.bd.datos_err))

        # Limpiar
        símismo.bd.borrar_archivo_datos()

    def test_exportar_datos_csv(símismo):
        símismo.bd.exportar_datos_csv()

        egresos = [os.path.join(os.path.abspath(''), símismo.bd.nombre + '_' + x + '.csv')
                   for x in ['ind', 'reg', 'error_reg']]

        símismo.assertTrue(all([os.path.isfile(x) for x in egresos]))

        # Limpiar
        for x in egresos:
            os.remove(x)

    def test_obt_datos(símismo):
        res = símismo.bd.obt_datos('completo')
        símismo.assertSetEqual(_a_conj(res, 'lugar'), {'701', '708', '7'})

        símismo.assertIn('completo', res)

    def test_obt_datos_de_lugar(símismo):
        res = símismo.bd.obt_datos('completo', lugares='708')
        símismo.assertTrue(_a_conj(res, 'lugar') == {'708'})

    def test_obt_datos_excluir_faltan(símismo):
        l_vars = ['completo', 'incompleto']
        res = símismo.bd.obt_datos(l_vars, excl_faltan=True)
        for var in l_vars:
            símismo.assertFalse(res.isnull()[var].values.any())

    def test_obt_datos_fecha_única(símismo):
        res = símismo.bd.obt_datos('completo', tiempos='2000')
        símismo.assertTrue(fechas_en_rango(res['tiempo'], ['2000-1-1'] * 2))

    def test_obt_datos_fecha_lista(símismo):
        res = símismo.bd.obt_datos('completo', tiempos=['2000', '2002'])
        símismo.assertTrue(fechas_en_lista(res['tiempo'], ['2000-01-01', '2002-01-01']))

    def test_obt_datos_fecha_rango(símismo):
        res = símismo.bd.obt_datos('completo', tiempos=('2000', '2002-6-1'))
        símismo.assertTrue(fechas_en_rango(res['tiempo'], ('2000-1-1', '2002-6-1')))

    def test_obt_datos_reg_con_interpol_no_necesario(símismo):
        res = símismo.bd.obt_datos('completo', tiempos=('2000', '2002-6-1'))
        símismo.assertTrue(res['completo'].values.shape[0] > 0)
        símismo.assertTrue(fechas_en_rango(res['tiempo'], ('2000-1-1', '2002-6-1')))

    def test_obt_datos_reg_fecha_única_con_interpol(símismo):
        res = símismo.bd.obt_datos(['incompleto', 'completo'], tiempos='2001')

        # Verificar interpolaciones
        vals = res.where(np.logical_and(res['lugar'] == '7', res['tiempo'] == np.datetime64('2001-01-01')), drop=True)
        npt.assert_allclose(vals['completo'].values, 2.500684)
        npt.assert_allclose(vals['incompleto'].values, 23.3394, rtol=0.001)

    def test_obt_datos_reg_fecha_rango_con_interpol(símismo):
        l_vars = ['incompleto', 'completo']
        res = símismo.bd.obt_datos(l_vars, tiempos=('2000', '2002-6-1'))
        for v in l_vars:
            símismo.assertTrue(res[v].values.shape[0] > 0)
            símismo.assertTrue(fechas_en_rango(res['tiempo'], ('2000-1-1', '2002-6-1')))

    def test_graficar(símismo):
        símismo.bd.graficar_hist('completo')
        símismo.assertTrue(os.path.isfile('./completo.jpg'))

    def test_graficar_línea(símismo):
        símismo.bd.graficar_línea(var='completo', archivo='línea completo.jpg')
        símismo.assertTrue(os.path.isfile('./línea completo.jpg'))

    def test_graficar_línea_fecha_única(símismo):
        símismo.bd.graficar_línea(var='completo', fechas='2000', archivo='línea fecha_única completo.jpg')
        símismo.assertTrue(os.path.isfile('./línea fecha_única completo.jpg'))

    def test_graficar_comparar(símismo):
        símismo.bd.graf_comparar(var_x='completo', var_y='incompleto')
        símismo.assertTrue(os.path.isfile('./completo_incompleto.jpg'))

    @classmethod
    def tearDownClass(cls):
        for c in os.walk('./'):
            for a in c[2]:
                nmbr, ext = os.path.splitext(a)
                try:
                    if ext in ['.jpg', '.jpeg', '.png']:
                        os.remove(a)
                except (FileNotFoundError, PermissionError):
                    pass


def _a_conj(bd, var):
    return set(np.unique(bd[var].values).tolist())


def lista_fechas_igual(l1, l2):
    lista_ls = [l1, l2]
    for i, l in enumerate(lista_ls):
        if not isinstance(l, np.ndarray):
            lista_ls[i] = np.array(obt_fecha_ft(l), dtype='datetime64')
        else:
            if not np.issubdtype(l.dtype, np.datetime64):
                lista_ls[i] = l.astype('datetime64')

    npt.assert_array_equal(lista_ls[0], lista_ls[1])


def fechas_en_lista(f, l):
    l = np.array(obt_fecha_ft(l), dtype='datetime64')

    return np.all(f.isin(l))


def fechas_en_rango(f, r):
    r = np.array(obt_fecha_ft(r), dtype='datetime64')

    return np.all(f <= r[1]) and np.all(f >= r[0])
