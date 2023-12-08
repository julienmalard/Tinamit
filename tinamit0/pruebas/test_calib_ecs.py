import os
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import scipy.stats as estad
from tinamit.calibs.ec import CalibradorEcOpt, CalibradorEcBayes
from tinamit.datos.bd import BD
from tinamit.datos.fuente import FuenteDic
from tinamit.geog.región import gen_lugares
from tinamit.ejemplos import obt_ejemplo

try:
    import pymc3 as pm
    import theano as thn
except ImportError:
    pm = thn = None

dir_act = os.path.split(__file__)[0]
arch_csv_geog = obt_ejemplo('geog_guate/geog_guate.csv')
arch_mds = os.path.join(dir_act, 'recursos/mds/prueba_para_calib.mdl')

calibradores = {'opt': CalibradorEcOpt, 'bayes': CalibradorEcBayes}
if pm is None or thn.configdefaults.rc != 0:  # saltar si no hay pymc3 o si no hay compilador c
    calibradores.pop('bayes')


class TestCalibrador(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        n_obs = 50
        datos_x = np.random.rand(n_obs)

        ec = 'y = a*x + b'
        cls.paráms = {'a': 2.4, 'b': -5}

        cls.clbrds = {ll: v(ec=ec, paráms=list(cls.paráms)) for ll, v in calibradores.items()}

        datos_y = cls.paráms['a'] * datos_x + cls.paráms['b'] + np.random.normal(0, 0.1, n_obs)
        cls.bd_datos = BD(
            fuentes=FuenteDic({'y': datos_y, 'x': datos_x, 'f': np.arange(n_obs)}, 'Datos generados', fechas='f')
        )

    def test_calibración_sencilla(símismo):
        líms = {
            'sin_líms': None,
            'un_lím': {'a': (0, None), 'b': (None, 0)},
            'dos_líms': {'a': (0, 10), 'b': (-10, -1)}
        }
        for nmbr, clbrd in símismo.clbrds.items():
            for lm in líms:
                with símismo.subTest(método=nmbr, líms=lm):
                    calibs = clbrd.calibrar(líms_paráms=líms[lm], bd=símismo.bd_datos)

                    est = [calibs[p]['cumbre'] for p in símismo.paráms]
                    val = list(símismo.paráms.values())
                    npt.assert_allclose(est, val, rtol=0.1)

    def test_calibrador_sin_var_y(símismo):
        with símismo.assertRaises(ValueError):
            CalibradorEcOpt(ec='a*x+b', paráms=list(símismo.paráms))


class TestCalibGeog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.paráms = prms = {
            'a': {'701': 3.4, '708': 3, '1001': 10},
            'b': {'701': -1.5, '708': -1.1, '1001': -3}
        }  # Nota: ¡a en (0, +inf) y b en (-inf, +inf) según los límites en el modelo externo!
        cls.ec = 'y = a*x + b'
        n_obs = {'701': 500, '708': 50, '1001': 500}
        datos_x = {lg: np.random.rand(n) for lg, n in n_obs.items()}
        datos_y = {
            lg: datos_x[lg] * prms['a'][lg] + prms['b'][lg] + np.random.normal(0, 0.1, n_obs[lg])
            for lg in n_obs
        }  # y = a*x + b
        lugares = [x for ll, v in datos_x.items() for x in [ll] * v.size]
        x = [i for v in datos_x.values() for i in v]
        y = [i for v in datos_y.values() for i in v]

        cls.clbrds = {ll: v(ec=cls.ec, paráms=['a', 'b']) for ll, v in calibradores.items()}

        fchs = pd.date_range(0, periods=len(x))
        cls.bd = BD(FuenteDic(
            {'lugar': lugares, 'x': x, 'y': y, 'f': fchs}, 'Datos geográficos', lugares='lugar', fechas='f'
        ))

        cls.lugar = gen_lugares(arch_csv_geog, nivel_base='País', nombre='Iximulew')

    def test_calibración_geog_con_escalas(símismo):
        """
        Calibramos una geografía con distintas escalas (municipios y departamentos).
        """
        líms_paráms = {'a': (0, 50)}
        for m in calibradores:
            with símismo.subTest(método=m):
                clbrd = calibradores[m](símismo.ec, paráms=['a', 'b'])
                calibs = clbrd.calibrar(símismo.bd, lugar=símismo.lugar, líms_paráms=líms_paráms)

                val = [símismo.paráms[p][lg] for p in símismo.paráms for lg in símismo.paráms[p]]
                if m == 'opt':
                    est = [calibs[lg][p]['cumbre'] for p in símismo.paráms for lg in símismo.paráms[p]]
                    npt.assert_allclose(val, est, rtol=0.2)
                else:
                    est = [calibs[lg][p]['dist'] for p in símismo.paráms for lg in símismo.paráms[p]]
                    símismo._verificar_aprox_bayes(val, est)

    def test_calibración_bayes_sin_mod_jerárquíco(símismo):
        """
        Calibramos en una geografía sin modelo jerárquico (región por región sin información a priori).
        """

        if 'bayes' in calibradores:
            calibs = símismo.clbrds['bayes'].calibrar(símismo.bd, lugar=símismo.lugar, jerárquico=False)
            val = [símismo.paráms[lg][p] for lg in símismo.paráms for p in símismo.paráms[lg]]
            est = [calibs[p][lg]['dist'] for lg in símismo.paráms for p in símismo.paráms[lg]]

            símismo._verificar_aprox_bayes(val, est)

    @staticmethod
    def _verificar_aprox_bayes(val, est, intvl=99):
        npt.assert_allclose([estad.percentileofscore(e, v) for e, v in zip(est, val)], 50, atol=intvl / 2)
