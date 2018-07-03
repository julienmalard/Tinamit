import datetime as ft
import os
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd

from tinamit.Análisis.Datos import DatosIndividuales, DatosRegión, SuperBD, leer_fechas

dir_act = os.path.split(__file__)[0]
arch_reg = os.path.join(dir_act, 'recursos/datos/datos_reg.csv')
arch_indiv = os.path.join(dir_act, 'recursos/datos/datos_indiv.csv')


class Test_GenerarDatos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bds = {
            'pandas': DatosIndividuales(
                'Pandas', pd.DataFrame(
                    {
                        'lugar': [708, 708, 7, 7, 7, 701],
                        'fecha': ['2000', '2002', '2000', '2002', '2003', '1990'],
                        'var_completo': [1, 2, 2, 3, 4, 0],
                        'var_incompleto': ['', 10, 20, '', 30, 15],
                        'temp': [1, 1, 1, 1, 1, 1]
                    }
                )
            ),
            'csv': DatosIndividuales('CSV', arch_indiv)
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
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2, 'jaja']}), cód_vacío='jaja')
        npt.assert_array_equal(bd.obt_datos('a')['a'], [1, 2, np.nan])

    def test_obt_datos_códigos_vacíos_múltiples(símismo):
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2, 'jaja', 'jajaja']}), cód_vacío='jaja')
        npt.assert_array_equal(bd.obt_datos('a', cód_vacío='jajaja')['a'], [1, 2, np.nan, np.nan])

    def test_fechas_columna(símismo):
        fechas = ['1947-8-14', '1947-8-15']
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2], 'f': fechas}), fecha='f')
        fechas_bd = bd.obt_datos('a')['fecha'].dt.date.tolist()
        símismo.assertListEqual(fechas_bd, leer_fechas(fechas))

    def test_fechas_ent(símismo):
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2]}), fecha=1966)
        fechas_bd = bd.obt_datos('a')['fecha'].dt.date.tolist()
        símismo.assertListEqual(fechas_bd, [ft.date(1966, 1, 1)] * 2)

    def test_fechas_ft(símismo):
        fecha = ft.date(1966, 1, 1)
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2]}), fecha=fecha)
        fechas_bd = bd.obt_datos('a')['fecha'].dt.date.tolist()
        símismo.assertListEqual(fechas_bd, [fecha] * 2)

    def test_fecha_texto(símismo):
        fecha = '1966-7-21'
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2]}), fecha=fecha)
        fechas_bd = bd.obt_datos('a')['fecha'].dt.date.tolist()
        símismo.assertListEqual(fechas_bd, [leer_fechas(fecha)] * 2)

    def test_fechas_error(símismo):
        with símismo.assertRaises(ValueError):
            DatosIndividuales('pueba', pd.DataFrame({'a': [1, 2]}), fecha='No soy una columna')

    def test_lugares_columna(símismo):
        lugar = ['1', '2']
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2], 'l': lugar}), lugar='l')
        lugares_bd = bd.obt_datos('a')['lugar'].tolist()
        símismo.assertListEqual(lugares_bd, lugar)

    def test_lugares_texto(símismo):
        bd = DatosIndividuales('prueba', pd.DataFrame({'a': [1, 2]}), lugar='708')
        lugares_bd = bd.obt_datos('a')['lugar'].tolist()
        símismo.assertListEqual(lugares_bd, ['708'] * 2)


class Test_SuperBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bd_región = DatosRegión(nombre='prueba regional', archivo=arch_reg, fecha='fecha', lugar='lugar')
        bd_indiv = DatosIndividuales(nombre='prueba individual', archivo=arch_indiv, fecha='fecha', lugar='lugar')
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
        bd_temp = DatosIndividuales(nombre='temp', archivo=arch_indiv, fecha='fecha', lugar='lugar')
        símismo.bd.conectar_datos(bd=bd_temp)
        símismo.bd.desconectar_datos(bd=bd_temp)
        símismo.assertNotIn(bd_temp.nombre, símismo.bd.bds)

    def test_guardar_cargar_datos(símismo):
        símismo.bd.guardar_datos()
        símismo.bd.cargar_datos()

        símismo.assertIn('completo', list(símismo.bd.variables))

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
        símismo.assertSetEqual(set(res['lugar'].unique().tolist()), {'701', '708', '7'})

        símismo.assertIn('completo', res)

    def test_obt_datos_de_lugar(símismo):
        res = símismo.bd.obt_datos('completo', lugares='708')
        símismo.assertTrue(set(res['lugar'].unique().tolist()) == {'708'})

    def test_obt_datos_excluir_faltan(símismo):
        res = símismo.bd.obt_datos(['completo', 'incompleto'], excl_faltan=True)
        símismo.assertFalse(res.isnull().values.any())

    def test_obt_datos_fecha_única(símismo):
        res = símismo.bd.obt_datos('completo', fechas=2000)
        símismo.assertTrue(all(res['fecha'] == '2000-1-1'))

    def test_obt_datos_fecha_lista(símismo):
        res = símismo.bd.obt_datos('completo', fechas=[2000, 2002])
        símismo.assertTrue(all(res['fecha'].isin(['2000-1-1', '2002-1-1'])))

    def test_obt_datos_fecha_rango(símismo):
        res = símismo.bd.obt_datos('completo', fechas=(2000, '2002-6-1'))
        símismo.assertTrue(all(res['fecha'] <= '2002-6-1') and all('2000-1-1' <= res['fecha']))

    def test_obt_datos_reg_con_interpol_no_necesario(símismo):
        res = símismo.bd.obt_datos('completo', fechas=(2000, '2002-6-1'), tipo='regional')
        símismo.assertTrue(res.shape[0] > 0)
        símismo.assertTrue(all(res['fecha'] <= '2002-6-1') and all('2000-1-1' <= res['fecha']))

    def test_obt_datos_reg_fecha_única_con_interpol(símismo):
        res = símismo.bd.obt_datos(['incompleto', 'completo'], fechas=2001, tipo='regional')

        # Verificar interpolaciones
        npt.assert_allclose(res.loc[res.lugar == '708'][res.fecha == '2001-1-1']['completo'].values, 1.500684)
        npt.assert_allclose(res.loc[res.lugar == '7'][res.fecha == '2001-1-1']['incompleto'].values, 23.3394,
                            rtol=0.001)

    def test_obt_datos_reg_fecha_rango_con_interpol(símismo):
        res = símismo.bd.obt_datos(['incompleto', 'completo'], fechas=(2000, '2002-6-1'), tipo='regional')
        símismo.assertTrue(res.shape[0] > 0)
        símismo.assertTrue(all(res['fecha'] <= '2002-6-1') and all('2000-1-1' <= res['fecha']))

    def test_graficar(símismo):
        símismo.bd.graficar_hist('completo')
        símismo.assertTrue(os.path.isfile('./completo.jpg'))

    def test_graficar_línea(símismo):
        símismo.bd.graficar_línea(var='completo', archivo='línea completo.jpg')
        símismo.assertTrue(os.path.isfile('./línea completo.jpg'))

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
