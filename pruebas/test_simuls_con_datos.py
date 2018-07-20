import os
import pandas as pd
import unittest

from Análisis.Datos import Datos
from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from tinamit.Geog import Geografía
from pruebas.test_mds import limpiar_mds

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_senc.mdl')


class Test_SimulConDatos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='días')
        cls.datos = pd.DataFrame()  # 20 días
        cls.datos_fecha = pd.DataFrame()  # 20 días

    def test_simular_datos_fecha(símismo):
        símismo.mod.simular(t_inic='01-01-2001', t_final='01-10-2001', bd=símismo.datos_fecha)

    def test_simular_datos_sin_fecha(símismo):
        símismo.mod.simular(t_inic=5, t_final=10, bd=símismo.datos)

    def test_simular_datos_fecha_sin_rango_tiempo(símismo):
        símismo.mod.simular(bd=símismo.datos_fecha)

    def test_simular_datos_sin_fecha_sin_rango_tiempo(símismo):
        símismo.mod.simular(bd=símismo.datos)

    def test_simular_datos_fecha_con_tiempo_inic(símismo):
        símismo.mod.simular(t_inic='01-01-2001', bd=símismo.datos_fecha)

    def test_simular_datos_fecha_con_tiempo_final(símismo):
        símismo.mod.simular(t_final='01-10-2001', bd=símismo.datos_fecha)

    def test_simular_datos_sin_fecha_con_tiempo_inic(símismo):
        símismo.mod.simular(t_inic=5, bd=símismo.datos)

    def test_simular_datos_sin_fecha_con_tiempo_final(símismo):
        símismo.mod.simular(t_final=10, bd=símismo.datos)

    def test_simular_datos_sin_fecha_tiempo_inic_fecha(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_inic='01-01-2002', bd=símismo.datos)

    def test_simular_datos_sin_fecha_tiempo_final_fecha(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final='01-01-2002', bd=símismo.datos)

    def test_simular_datos_fecha_tiempo_inic_numérico(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_inic=10, bd=símismo.datos_fecha)

    def test_simular_datos_fecha_tiempo_final_numérico(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final=10, bd=símismo.datos_fecha)

    def test_simuluar_datos_vars_inic(símismo):
        símismo.mod.simular(t_final=10, bd=símismo.datos, vars_inic='Nivel lago inicial')

    def test_simuluar_datos_vars_extern(símismo):
        símismo.mod.simular(t_final=10, bd=símismo.datos, vars_extern='Lluvia')

    def test_simuluar_datos_corresp_vars(símismo):
        símismo.mod.simular(t_final=10, bd=símismo.datos, vars_inic={'Nivel lago inicial': 'Nivel lago inicial2'})

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


class Test_SimulConDatosGeog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='días')
        cls.geog = Geografía()
        cls.datos = Datos()

    def test_simular_en_lugar_único(símismo):
        símismo.mod.simular(t_final=10, en='7', geog=símismo.geog, bd=símismo.datos)

    def test_simular_en_lugar_con_escala(símismo):
        símismo.mod.simular(t_final=10, en='7', escala='municipio', geog=símismo.geog, bd=símismo.datos)

    def test_simular_en_lugar_sin_geog(símismo):
        símismo.mod.simular(t_final=10, en='7', bd=símismo.datos)

    def test_simular_en_lugar_con_escala_sin_geog(símismo):
        with símismo.assertRaises(ValueError):
            símismo.mod.simular(t_final=10, en='7', escala='municipio', bd=símismo.datos)

    def test_simular_en_lugar_sin_datos(símismo):
        símismo.mod.simular(t_final=10, en='7', escala='municipio', bd=símismo.datos)

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()
