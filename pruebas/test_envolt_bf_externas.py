import inspect
import unittest

import numpy.testing as npt

import tinamit.EnvolturasBF
from tinamit.BF import ModeloBF

@unittest.skip
class Test_EnvolturasBF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloBF):
                cls.envolturas_disp[nombre] = obj

    def test_envolturas_incluídas(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                obj.verificar(símismo)
