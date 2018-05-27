import tinamit.EnvolturasBF

from tinamit.BF import ModeloBF, EnvolturaBF
import inspect
import unittest


class Test_EnvolturasBF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloBF):
                cls.envolturas_disp[nombre] = obj

    def test_leer_escribir_ingresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                return
                # EnvolturaBF(obj).comprobar_leer_escribir_ingresos()

    def test_comprobar_leer_egresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                return
                # EnvolturaBF(obj).comprobar_leer_egresos()
