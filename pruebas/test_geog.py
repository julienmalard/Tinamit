import datetime as ft
import os
import unittest

import numpy as np
import numpy.testing as npt

from tinamit.geog.región import Nivel, Lugar, gen_nivel

dir_act = os.path.split(__file__)[0]
arch_csv_geog = os.path.join(dir_act, 'recursos/datos/prueba_geog.csv')
arch_frm_regiones = os.path.join(dir_act, 'recursos/frm/munis.shp')
arch_frm_otra = os.path.join(dir_act, 'recursos/frm/otra_frm.shp')
arch_clim_diario = os.path.join(dir_act, 'recursos/datos/clim_diario.csv')
arch_clim_mensual = os.path.join(dir_act, 'recursos/datos/clim_mensual.csv')
arch_clim_anual = os.path.join(dir_act, 'recursos/datos/clim_anual.csv')


class TestRegión(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        muni = Nivel('Municipio')
        dept = Nivel('Departamento', subniveles=muni)
        terr = Nivel('Territorio', subniveles=muni)
        país = Nivel('País', subniveles=[dept, terr])
        muni1, muni2, muni3 = [Lugar('Muni%i' % i, nivel=muni, cód='M' + str(i)) for i in range(1, 4)]

        dept1 = Lugar('Dept1', nivel=dept, cód='D1', sub_lugares=[muni1, muni2])
        dept2 = Lugar('Dept2', nivel=dept, cód='D2', sub_lugares=[muni3])
        terr1 = Lugar('Terr1', nivel=terr, cód='T1', sub_lugares=[muni1])
        terr2 = Lugar('Terr2', nivel=terr, cód='T2', sub_lugares=[muni2])
        cls.guate = Lugar(
            'Guatemala', sub_lugares={muni1, muni2, muni3, dept1, dept2, terr1, terr2},
            nivel=país
        )

        cls.munis = {'1': muni1, '2': muni2, '3': muni3}
        cls.depts = {'1': dept1, '2': dept2}
        cls.terrs = {'1': terr1, '2': terr2}

    def test_obt_lugares(símismo):
        símismo.assertSetEqual(
            símismo.guate.lugares(),
            {símismo.guate, *símismo.munis.values(), *símismo.depts.values(), *símismo.terrs.values()}
        )

    def test_obt_lugares_con_nivel(símismo):
        símismo.assertSetEqual(símismo.guate.lugares(nivel='Municipio'), set(símismo.munis.values()))

    def test_obt_lugares_en(símismo):
        símismo.assertSetEqual(
            símismo.guate.lugares(en='D1', nivel='Municipio'),
            símismo.depts['1'].sub_lugares
        )

    def test_obt_lugares_donde_no_hay(símismo):
        símismo.assertSetEqual(
            símismo.guate.lugares(en='D1', nivel='Territorio'),
            set()
        )

    def test_buscar_de_código(símismo):
        símismo.assertEqual(símismo.guate['M1'], símismo.munis['1'])

    def test_buscar_de_nombre(símismo):
        símismo.assertEqual(símismo.guate.buscar_nombre('Muni1'), símismo.munis['1'])

    def test_buscar_código_no_existe(símismo):
        with símismo.assertRaises(ValueError):
            símismo.guate.buscar_nombre('Hola, yo no existo.')


class TestGenAuto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nivel = gen_nivel(arch_csv_geog, nivel_base='País', nombre='Iximulew')


class TestMapa(unittest.TestCase):
    def test_dibujar_desde_matriz_np(símismo):
        pass


class Test_Geografía(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.geog = Geografía(nombre='Prueba Guatemala')
        cls.geog.espec_estruct_geog(archivo=arch_csv_geog)

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

    def test_dibujar_desde_matriz_np_sin_estruct_con_ids(símismo):
        geog = Geografía(nombre='Prueba Guatemala')
        geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI', escala_geog='municipio')
        lugares = geog.formas_reg['municipio']['ids']
        geog.dibujar(archivo='prueba.jpg', valores=np.random.rand(len(lugares)), ids=lugares[::-1])
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
