import os
import unittest

from pruebas.recursos.BF.prueba_bf import ModeloPrueba
from tinamit.Geog import Geografía
from pruebas.test_mds import limpiar_mds

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_senc.mdl')


@unittest.skip
class Test_SimulConDatosBD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = ModeloPrueba(unid_tiempo='días')

    def test_simular_con_BD(símismo):
        datos = pd.DataFrame()  # 100 días
        mod.conectar_datos(datos)
        mod.simular(t_inic=10, t_final=50)
        mod.simular(t_inic=10)
        mod.desconectar_datos(datos)

        datos = pd.DataFrame()  # Con fechas
        mod.conectar_datos(datos)
        mod.simular(t_inic='01-01-2001', t_final=100)
        mod.simular(t_inic='01-01-2001', t_final='01-01-2002')
        mod.simular(t_inic=1, t_final='01-01-2002')  # error
        mod.simular(t_final='01-01-2002')
        mod.simular(t_inic=100)
        mod.desconectar_datos()

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


@unittest.skip
class Test_SimulConDatosYGeog(unittest.TestCase):
    def test_(símismo):
        geog = Geografía()
        datos = ()
        mod.conectar_geog(geog)
        mod.conectar_datos(datos)
        mod.simular(t_final='01-01-2002', en='7')
        mod.simular(t_final=10, en='7')

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()
