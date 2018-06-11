import numpy.testing as npt
import os
import unittest

import numpy as np
import pandas as pd

from pruebas.test_mds import limpiar_mds
from tinamit.Análisis.Calibs import Calibrador
from tinamit.Análisis.Datos import DatosIndividuales, SuperBD
from tinamit.EnvolturasMDS.PySD import ModeloPySD
from tinamit.Geog.Geog import Geografía

try:
    import pymc3 as pm
except ImportError:
    pm = None

dir_act = os.path.split(__file__)[0]
arch_csv_geog = os.path.join(dir_act, 'recursos/prueba_geog.csv')
arch_mds = os.path.join(dir_act, 'recursos/prueba_para_calib.mdl')

métodos = ['optimizar']
if pm is not None:
    métodos.append('inferencia bayesiana')


class Test_Calibrador(unittest.TestCase):
    ec = 'y = a*x + b'
    paráms = {'a': 2.4, 'b': -5}
    clbrd = Calibrador(ec=ec)

    @classmethod
    def setUpClass(cls):
        n_obs = 100
        datos_x = np.random.rand(n_obs)

        datos_y = cls.paráms['a'] * datos_x + cls.paráms['b'] + np.random.rand(n_obs) * 0.01
        bd_pds = pd.DataFrame({'y': datos_y, 'x': datos_x})
        bd_datos = DatosIndividuales('Datos Generados', bd_pds)

        cls.bd_datos = SuperBD(nombre='BD Principal', bds=bd_datos)
        cls.bd_datos.espec_var('x')
        cls.bd_datos.espec_var('y')

    def test_calibración_sencilla(símismo):
        for m in métodos:
            with símismo.subTest(método=m):
                calibs = símismo.clbrd.calibrar(método=m, bd_datos=símismo.bd_datos)
                for p, v in símismo.paráms.items():
                    símismo.assertAlmostEquals(calibs[p]['val'], v, places=1)


class Test_CalibEnModelo(unittest.TestCase):
    paráms = {
        '701': {'Factor a': 3.4, 'Factor b': -1.5},
        '708': {'Factor a': 3, 'Factor b': -1.1},
        '1001': {'Factor a': 10, 'Factor b': -3},
    }

    @classmethod
    def setUpClass(cls):
        n_obs = {'701': 500, '708': 50, '1001': 500}
        datos_x = {lg: np.random.rand(n) for lg, n in n_obs.items()}
        datos_y = {lg: datos_x[lg] * d['Factor a'] + d['Factor b'] + np.random.rand(n_obs[lg]) * 0.1
                   for lg, d in cls.paráms.items()}  # y = a*x + b
        lugares = [x for ll, v in datos_x.items() for x in [ll] * v.size]
        x = [i for v in datos_x.values() for i in v]
        y = [i for v in datos_y.values() for i in v]
        bd_pds = DatosIndividuales('Datos geográficos', pd.DataFrame({'lugar': lugares, 'x': x, 'y': y}),
                                   lugar='lugar')

        geog = Geografía('Geografía Iximulew', arch_csv_geog)
        cls.bd = SuperBD('BD Central', bd_pds, geog=geog)
        cls.bd.espec_var('x')
        cls.bd.espec_var('y')

        cls.mod = ModeloPySD(arch_mds)
        cls.mod.conectar_datos(cls.bd)
        cls.mod.conectar_var_a_datos('X', var_bd='x')
        cls.mod.conectar_var_a_datos('Y', var_bd='y')

    def test_calibración_geog_con_escalas(símismo):
        """
        Calibramos una geografía con distintas escalas (municipios y departamentos).
        """

        for m in métodos:
            with símismo.subTest(método=m):
                símismo.mod.especificar_micro_calib(var='Y', método=m)
                símismo.mod.efectuar_micro_calibs()

                val = [símismo.paráms[lg][p] for lg in símismo.paráms for p in símismo.paráms[lg]]
                est = [símismo.mod.calibs[p][lg]['val'] for lg in símismo.paráms for p in símismo.paráms[lg]]

                npt.assert_allclose(est, val, rtol=0.1)

                símismo.mod.borrar_micro_calib('Y')

    def test_calibración_bayes_sin_mod_jerárquíco(símismo):
        if 'inferencia bayesiana' in métodos:
            símismo.mod.especificar_micro_calib(
                var='Y', método='inferencia bayesiana', ops_método={'mod_jerárquico': False}
            )
            símismo.mod.efectuar_micro_calibs()

            val = [símismo.paráms[lg][p] for lg in símismo.paráms for p in símismo.paráms[lg]]
            est = [símismo.mod.calibs[p][lg]['val'] for lg in símismo.paráms for p in símismo.paráms[lg]]

            npt.assert_allclose(est, val, rtol=0.1)

            símismo.mod.borrar_micro_calib('Y')

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()
