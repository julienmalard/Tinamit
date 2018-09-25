import inspect
import unittest

import numpy.testing as npt

import tinamit.EnvolturasBF
from tinamit.BF import ModeloBF


class Test_EnvolturasBF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloBF):
                cls.envolturas_disp[nombre] = obj()

    def test_leer_ingresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):

                d_ref = obj.cargar_ref_ejemplo_vals_inic()

                for v in obj.variables:
                    act = obj.variables[v]['val']
                    ref = d_ref[v]['val']
                    npt.assert_equal(ref, act, err_msg=v)
