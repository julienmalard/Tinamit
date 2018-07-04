import os
import unittest

from tinamit.Geog import Geografía
from tinamit.EnvolturasMDS import generar_mds
from tinamit.Geog import Lugar
from pruebas.test_geog import arch_clim_diario
from pruebas.test_mds import limpiar_mds

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_senc.mdl')


class Test_SimulConClima(unittest.TestCase):

    def test_simular_con_datos_clima(símismo):
        mod = generar_mds(arch_mds)
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_diarios(arch_clim_diario, cols_datos={'Precipitación': 'Lluvia'},
                               conv={'Precipitación': 1}, c_fecha='Fecha')
        mod.conectar_var_clima(var='Lluvia', var_clima='Precipitación', conv=1)
        res = mod.simular(t_final=1, t_inic='1-1-2018', lugar_clima=lugar, vars_interés='Lluvia')
        símismo.assertEqual(res['Lluvia'][0], 15)

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()


@unittest.skip
class Test_SimulConDatosBD(unittest.TestCase):
    def test_simular_con_BD(símismo):
        
        mod = generar_mds(arch_mds)
        datos = pd.DataFrame()  # 100 días
        mod.conectar_datos(datos)
        mod.simular(t_inic=10, t_final=50)
        mod.simular()
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

    def test_simular_con_datos_clima(símismo):
        datos = ''
        mod.conectar_datos(datos)
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_de(datos)
        mod.simular(t_inic='01-01-2001', t_final=365, lugar_clima=lugar)

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
