import inspect
import os
import unittest

import numpy.testing as npt

import tinamit.EnvolturasBF
from tinamit.BF import ModeloBF, ModeloImpaciente


class Test_EnvolturasBF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloBF):
                cls.envolturas_disp[nombre] = obj()

    def test_dic_vars(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                ll_necesarias = ['val', 'unidades', 'ingreso', 'egreso', 'dims', 'líms', 'info']
                símismo.assertTrue(all(all(x in d_v for x in ll_necesarias) for d_v in obj.variables.values()))

    def test_leer_ingresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):

                d_ref = obj.cargar_ref_ejemplo_vals_inic()

                for v in obj.variables:
                    act = obj.variables[v]['val']
                    ref = d_ref[v]['val']
                    npt.assert_equal(ref, act)


class Test_Envolturas_ModeloImpaciente(unittest.TestCase):
    arch_prb_escrb_ingr = 'prueba_ingr.txt'

    @classmethod
    def setUpClass(cls):
        cls.envolturas_disp = {}
        for nombre, obj in inspect.getmembers(tinamit.EnvolturasBF):
            if inspect.isclass(obj) and issubclass(obj, ModeloImpaciente):
                cls.envolturas_disp[nombre] = obj()

    def test_escribir_ingresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                obj.escribir_ingr(n_años_simul=1, archivo=símismo.arch_prb_escrb_ingr)
                obj.leer_archivo_vals_inic(archivo=símismo.arch_prb_escrb_ingr)

                d_ref = obj.cargar_ref_ejemplo_vals_inic()

                for v in obj.variables:
                    act = obj.variables[v]['val']
                    ref = d_ref[v]['val']
                    npt.assert_equal(ref, act)

    def test_leer_egresos(símismo):
        for nmb, obj in símismo.envolturas_disp.items():
            with símismo.subTest(envlt=nmb):
                if obj.prb_arch_egr is not None:
                    dic_ref = obj.cargar_ref_ejemplo_egr()

                    dic_egr = obj.leer_archivo_egr(n_años_egr=1, archivo=obj.prb_arch_egr)

                    for v, val in dic_egr.items():
                        ref = dic_ref[v]
                        npt.assert_equal(val, ref)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.arch_prb_escrb_ingr):
            os.remove(cls.arch_prb_escrb_ingr)
