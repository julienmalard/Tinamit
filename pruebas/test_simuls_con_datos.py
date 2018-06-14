import os
import unittest

from tinamit.EnvolturasMDS import generar_mds
from tinamit.Geog import Lugar
from pruebas.test_geog import arch_clim_diario
from pruebas.test_mds import limpiar_mds

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/prueba_senc.mdl')


class Test_SimulConClima(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mod = generar_mds(arch_mds)

    def test_simular_con_datos_clima(símismo):
        lugar = Lugar(lat=0, long=0, elev=0)
        lugar.observar_diarios(arch_clim_diario, cols_datos={'Precipitación': 'Lluvia'},
                               conv={'Precipitación': 1}, c_fecha='Fecha')
        símismo.mod.conectar_var_clima(var='Lluvia', var_clima='Precipitación', conv=1)
        res = símismo.mod.simular(tiempo_final=1, fecha_inic='1-1-2018', lugar=lugar, vars_interés='Lluvia')
        símismo.assertEqual(res['Lluvia'][0], 15)

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()
