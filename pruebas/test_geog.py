import datetime as ft
import os
import unittest

import numpy as np
import numpy.testing as npt

from tinamit.Geog.Geog import Geografía, Lugar

dir_act = os.path.split(__file__)[0]
arch_csv_geog = os.path.join(dir_act, 'recursos/datos/prueba_geog.csv')
arch_frm_regiones = os.path.join(dir_act, 'recursos/frm/munis.shp')
arch_frm_otra = os.path.join(dir_act, 'recursos/frm/otra_frm.shp')
arch_clim_diario = os.path.join(dir_act, 'recursos/datos/clim_diario.csv')
arch_clim_mensual = os.path.join(dir_act, 'recursos/datos/clim_mensual.csv')
arch_clim_anual = os.path.join(dir_act, 'recursos/datos/clim_anual.csv')


class Test_Geografía(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.geog = Geografía(nombre='Prueba Guatemala')
        cls.geog.espec_estruct_geog(archivo=arch_csv_geog)

    def test_nombre_a_cód_no_ambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Panajachel')
        símismo.assertEqual(cód, '710')

    def test_nombre_a_cód_ambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Sololá')
        símismo.assertIn(cód, ['7', '701'])

    def test_nombre_a_cód_desambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Sololá', escala='departamento')
        símismo.assertEqual(cód, '7')

    def test_nombre_a_cód_erróneo(símismo):
        with símismo.assertRaises(ValueError):
            símismo.geog.nombre_a_cód(nombre='¡Yo no existo!')

    def test_obt_lugares_en_región_con_escala(símismo):
        lgs = símismo.geog.obt_lugares_en('7', escala='municipio')
        símismo.assertEqual(len(lgs), 19)
        símismo.assertTrue(all(símismo.geog.en_región(lg, '7') for lg in lgs))

    def test_obt_lugares_en_región_sin_escala(símismo):
        """Debe devolver la misma región."""
        lgs = símismo.geog.obt_lugares_en('7')
        símismo.assertListEqual(lgs, ['7'])

    def test_obt_lugares_en_región_cód_numérico(símismo):
        ref = símismo.geog.obt_lugares_en('1', escala='municipio')
        lgs = símismo.geog.obt_lugares_en(1, escala='municipio')
        símismo.assertListEqual(ref, lgs)

    def test_obt_lugares_en_nada_con_escala(símismo):
        """
        Con `en==None` y escala especificada, nos devuelve todos los lugares de la escala especificada en la
        geografía.
        """
        lgs = símismo.geog.obt_lugares_en(escala='departamento')
        símismo.assertListEqual(lgs, [str(x) for x in range(1, 23)])

    def test_obt_lugares_en_con_escala_errónea(símismo):
        with símismo.assertRaises(ValueError):
            símismo.geog.obt_lugares_en(escala='¡Yo soy una escala que no existe!')

    def test_obt_todos_lugares(símismo):
        lgs = símismo.geog.obt_todos_lugares_en()
        símismo.assertTrue(all(x in lgs for x in ['7', '701', '708', 'T1']))

    def test_obt_todos_lugares_en_región(símismo):
        lgs = símismo.geog.obt_todos_lugares_en(en='7')
        símismo.assertSetEqual(set(lgs), set(str(x) for x in range(701, 720)))

    def test_obt_jerarquía(símismo):
        jrq = símismo.geog.obt_jerarquía(escala='municipio')
        munis = símismo.geog.obt_lugares_en(escala='municipio')
        trtrs = símismo.geog.obt_lugares_en(escala='territorio')
        deptos = símismo.geog.obt_lugares_en(escala='departamento')

        símismo.assertTrue(set(munis + trtrs).issubset(set(jrq)) or set(munis + deptos).issubset(set(jrq)))
        símismo.assertTrue(all([jrq[x] is None for x in jrq if x not in munis]))

    def test_obt_jerarquía_con_orden(símismo):
        jrq = símismo.geog.obt_jerarquía(escala='municipio', orden_jerárquico=['departamento'])
        munis = símismo.geog.obt_lugares_en(escala='municipio')
        deptos = símismo.geog.obt_lugares_en(escala='departamento')

        símismo.assertTrue(set(munis + deptos).issubset(set(jrq)))
        símismo.assertTrue(all([jrq[d] is None for d in deptos]))

    def test_agregar_y_quitar_forma(símismo):
        símismo.geog.agregar_forma(arch_frm_otra, nombre='bosque')
        símismo.assertIn('bosque', símismo.geog.formas)
        símismo.geog.quitar_forma('bosque')
        símismo.assertNotIn('bosque', símismo.geog.formas)

    def test_agregar_y_quitar_forma_regiones(símismo):
        geog = Geografía(nombre='Prueba Guatemala')
        geog.espec_estruct_geog(archivo=arch_csv_geog)
        geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI')

        símismo.assertIn('municipio', geog.formas_reg)
        geog.quitar_forma('municipio')
        símismo.assertNotIn('municipio', geog.formas_reg)

    def test_dibujar_desde_matriz_np(símismo):
        símismo.geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI')
        lugares = símismo.geog.obt_lugares_en(escala='municipio')
        símismo.geog.dibujar(archivo='prueba.jpg', valores=np.random.rand(len(lugares)), ids=lugares)
        símismo.assertTrue(os.path.isfile('prueba.jpg'))
        os.remove('prueba.jpg')

    def test_dibujar_desde_matriz_np_sin_ids(símismo):
        símismo.geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI')
        lugares = símismo.geog.obt_lugares_en(escala='municipio')
        símismo.geog.dibujar(archivo='prueba.jpg', valores=np.random.rand(len(lugares)))
        símismo.assertTrue(os.path.isfile('prueba.jpg'))
        os.remove('prueba.jpg')

    def test_dibujar_desde_matriz_np_sin_estruct(símismo):
        geog = Geografía(nombre='Prueba Guatemala')
        geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI', escala_geog='municipio')
        lugares = geog.formas_reg['municipio']['ids']
        geog.dibujar(archivo='prueba.jpg', valores=np.random.rand(len(lugares)))
        os.remove('prueba.jpg')


class Test_Lugar(unittest.TestCase):
    def test_observar_diarios(símismo):
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_diarios(arch_clim_diario, cols_datos={'Precipitación': 'Lluvia'},
                               conv={'Precipitación': 1}, c_fecha='Fecha')
        f_inic = ft.datetime(2018, 1, 1).date()
        f_final = ft.datetime(2018, 1, 31).date()
        lugar.prep_datos(fecha_inic=f_inic, fecha_final=f_final)
        res = lugar.devolver_datos('Precipitación', f_inic=f_inic, f_final=f_final)
        npt.assert_array_equal(res['Precipitación'], [1] * 15 + [0] * 16)

    def test_comb_datos(símismo):
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_diarios(arch_clim_diario, cols_datos={'Precipitación': 'Lluvia'},
                               conv={'Precipitación': 1}, c_fecha='Fecha')
        f_inic = ft.datetime(2018, 1, 1).date()
        f_final = ft.datetime(2018, 1, 31).date()
        lugar.prep_datos(fecha_inic=f_inic, fecha_final=f_final)
        res = lugar.comb_datos('Precipitación', combin='total', f_inic=f_inic, f_final=f_final)
        símismo.assertEqual(res['Precipitación'], 15)

    def test_observar_mensuales(símismo):
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_mensuales(arch_clim_mensual, cols_datos={'Precipitación': 'Lluvia'},
                                 conv={'Precipitación': 1}, meses='Mes', años='Año')
        f_inic = ft.datetime(2018, 1, 1).date()
        f_final = ft.datetime(2018, 1, 31).date()
        lugar.prep_datos(fecha_inic=f_inic, fecha_final=f_final)
        res = lugar.devolver_datos('Precipitación', f_inic=f_inic, f_final=f_final)
        npt.assert_array_equal(res['Precipitación'], np.ones(31))

    def test_observar_anuales(símismo):
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_anuales(arch_clim_anual, cols_datos={'Precipitación': 'Lluvia'},
                               conv={'Precipitación': 1}, años='Año')
        f_inic = ft.datetime(2018, 1, 1).date()
        f_final = ft.datetime(2018, 1, 31).date()
        lugar.prep_datos(fecha_inic=f_inic, fecha_final=f_final)
        res = lugar.devolver_datos('Precipitación', f_inic=f_inic, f_final=f_final)
        npt.assert_array_equal(res['Precipitación'], np.ones(31))
