import os
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import scipy.stats as estad
from pruebas.test_mds import limpiar_mds
from tinamit.Análisis.Calibs import CalibradorEc
from tinamit.Análisis.Datos import MicroDatos, SuperBD
from tinamit.EnvolturasMDS.PySD import ModeloPySD
from tinamit.Geog.Geog import Geografía

try:
    import pymc3 as pm
    import theano as T
except ImportError:
    pm = T = None

if T is None:
    hay_compil_c = False
else:
    hay_compil_c = T.configdefaults.rc == 0


dir_act = os.path.split(__file__)[0]
arch_csv_geog = os.path.join(dir_act, 'recursos/datos/prueba_geog.csv')
arch_mds = os.path.join(dir_act, 'recursos/MDS/prueba_para_calib.mdl')

métodos = ['optimizar']
if pm is not None and hay_compil_c:
    métodos.append('inferencia bayesiana')


class Test_Calibrador(unittest.TestCase):
    ec = 'y = a*x + b'
    paráms = {'a': 2.4, 'b': -5}
    clbrd = CalibradorEc(ec=ec)

    @classmethod
    def setUpClass(cls):
        n_obs = 50
        datos_x = np.random.rand(n_obs)

        datos_y = cls.paráms['a'] * datos_x + cls.paráms['b'] + np.random.normal(0, 0.1, n_obs)
        bd_pds = pd.DataFrame({'y': datos_y, 'x': datos_x})
        bd_datos = MicroDatos('Datos Generados', bd_pds)

        cls.bd_datos = SuperBD(nombre='BD Principal', bds=bd_datos)
        cls.bd_datos.espec_var('x')
        cls.bd_datos.espec_var('y')

    def test_calibración_sencilla(símismo):
        for m in métodos:
            with símismo.subTest(método=m):
                calibs = símismo.clbrd.calibrar(método=m, bd_datos=símismo.bd_datos)
                for p, v in símismo.paráms.items():
                    símismo.assertAlmostEqual(calibs[p]['val'], v, places=1)

    def test_calibrador_sin_var_y(símismo):
        with símismo.assertRaises(ValueError):
            CalibradorEc(ec='a*x+b')

    def test_error_líms(símismo):
        with símismo.assertRaises(ValueError):
            símismo.clbrd.calibrar(bd_datos=símismo.bd_datos, líms_paráms={'a': (1, 2, 3)})

    def test_calibrar_en_sin_geog(símismo):
        with símismo.assertRaises(ValueError):
            símismo.clbrd.calibrar(bd_datos=símismo.bd_datos, en='1')


class Test_CalibEnModelo(unittest.TestCase):
    paráms = {
        '701': {'Factor a': 3.4, 'Factor b': -1.5},
        '708': {'Factor a': 3, 'Factor b': -1.1},
        '1001': {'Factor a': 10, 'Factor b': -3},
    }  # Nota: ¡a en (0, +inf) y b en (-inf, +inf) según los límites en el modelo externo!

    @classmethod
    def setUpClass(cls):
        n_obs = {'701': 500, '708': 50, '1001': 500}
        datos_x = {lg: np.random.rand(n) for lg, n in n_obs.items()}
        datos_y = {lg: datos_x[lg] * d['Factor a'] + d['Factor b'] + np.random.normal(0, 0.5, n_obs[lg])
                   for lg, d in cls.paráms.items()}  # y = a*x + b
        lugares = [x for ll, v in datos_x.items() for x in [ll] * v.size]
        x = [i for v in datos_x.values() for i in v]
        y = [i for v in datos_y.values() for i in v]
        bd_pds = MicroDatos('Datos geográficos', pd.DataFrame({'lugar': lugares, 'x': x, 'y': y}),
                            lugar='lugar')

        cls.geog = Geografía('Geografía Iximulew', arch_csv_geog)
        cls.bd = SuperBD('BD Central', bd_pds)

        cls.mod = ModeloPySD(arch_mds)

    def test_calibración_geog_con_escalas(símismo):
        """
        Calibramos una geografía con distintas escalas (municipios y departamentos).
        """

        for m in métodos:
            with símismo.subTest(método=m):
                símismo.mod.especificar_micro_calib(var='Y', método=m)
                símismo.mod.efectuar_micro_calibs(bd=símismo.bd, geog=símismo.geog, corresp_vars={'X': 'x', 'Y': 'y'})

                val = [símismo.paráms[lg][p] for lg in símismo.paráms for p in símismo.paráms[lg]]
                if m == 'optimizar':
                    est = [símismo.mod.calibs[p][lg]['val'] for lg in símismo.paráms for p in símismo.paráms[lg]]
                    npt.assert_allclose(val, est, rtol=0.2)
                    símismo.mod.borrar_micro_calib('Y')
                else:
                    est = [símismo.mod.calibs[p][lg]['dist'] for lg in símismo.paráms for p in símismo.paráms[lg]]
                    símismo.mod.borrar_micro_calib('Y')
                    símismo._verificar_aprox_bayes(val, est, intvl=80)

    def test_calibración_bayes_sin_mod_jerárquíco(símismo):
        """
        Calibramos en una geografía sin modelo jerárquico (región por región sin información a priori).
        """

        if 'inferencia bayesiana' in métodos:
            símismo.mod.especificar_micro_calib(
                var='Y', método='inferencia bayesiana', ops_método={'mod_jerárquico': False}
            )
            símismo.mod.efectuar_micro_calibs(bd=símismo.bd, geog=símismo.geog, corresp_vars={'X': 'x', 'Y': 'y'})

            val = [símismo.paráms[lg][p] for lg in símismo.paráms for p in símismo.paráms[lg]]
            est = [símismo.mod.calibs[p][lg]['dist'] for lg in símismo.paráms for p in símismo.paráms[lg]]

            símismo.mod.borrar_micro_calib('Y')
            símismo._verificar_aprox_bayes(val, est)

    def test_guardar_cargar_calibs(símismo):
        símismo.mod.especificar_micro_calib(var='Y', método='optimizar')
        símismo.mod.efectuar_micro_calibs(bd=símismo.bd, geog=símismo.geog, corresp_vars={'X': 'x', 'Y': 'y'})
        calibs = símismo.mod.calibs.copy()
        símismo.mod.guardar_calibs()
        símismo.mod.borrar_calibs()
        símismo.mod.cargar_calibs()
        os.remove('mds_calibs.json')
        símismo.assertDictEqual(calibs, símismo.mod.calibs)

    @staticmethod
    def _verificar_aprox_bayes(val, est, intvl=90):
        npt.assert_allclose([estad.percentileofscore(e, v) for e, v in zip(est, val)], 50, atol=intvl / 2)

    @classmethod
    def tearDownClass(cls):

        limpiar_mds()
