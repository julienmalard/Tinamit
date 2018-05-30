import unittest

import numpy as np
import pandas as pd

from tinamit.Análisis.Calibs import Calibrador
from tinamit.Análisis.Datos import DatosIndividuales, SuperBD

métodos = ['optimizar', 'inferencia bayesiana']

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
    def test_calibración_jerárquíca(símismo):
        for m in métodos:
            with símismo.subTest(método=m):
                pass

    def test_calibración_bayes_mod_jerárquíco(símismo):
        for m in métodos:
            with símismo.subTest(método=m):
                pass
