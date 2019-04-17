import inspect
import unittest

import numpy.testing as npt

from tinamit.envolt import bf


class Test_EnvolturasBF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(bf):
            if inspect.isclass(obj) and issubclass(obj, bf.EnvolturaBF):
                cls.envolturas_disp[nombre] = obj

    def test_envolturas_incluídas(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                obj.verificar(símismo)
