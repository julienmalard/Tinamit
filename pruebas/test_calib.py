import unittest

import numpy as np
import pandas as pd

from tinamit.Análisis.Calibs import Calibrador
from tinamit.Análisis.Datos import DatosIndividuales, SuperBD


class Test_Calibrador(unittest.TestCase):
    # métodos = ['optimizar', 'inferencia bayesiana']
    métodos = ['optimizar']
    ec = 'y = a*x + b'
    paráms = {'a': 2.4, 'b': -5}
    clbrd = Calibrador(ec=ec)

    @classmethod
    def setUpClass(cls):
        datos_x = np.random.rand(100)
        datos_y = cls.paráms['a'] * datos_x + cls.paráms['b'] + np.random.rand(100) * 0.01
        bd_pds = pd.DataFrame({'y': datos_y, 'x': datos_x})
        bd_datos = DatosIndividuales('Datos Generados', bd_pds)

        cls.bd_datos = SuperBD(nombre='BD Principal', bds=bd_datos)
        cls.bd_datos.espec_var('x')
        cls.bd_datos.espec_var('y')

    def test_calibración_sencilla(símismo):
        for m in símismo.métodos:
            with símismo.subTest(método=m):
                calibs = símismo.clbrd.calibrar(método=m, bd_datos=símismo.bd_datos)
                for p, v in símismo.paráms.items():
                    símismo.assertAlmostEquals(calibs[p]['val'], v, places=1)
