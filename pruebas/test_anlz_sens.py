import unittest
import numpy as np
import numpy.testing as npt

from tinamit.Análisis.Sens.corridas import gen_vals_inic
from tinamit.Análisis.Sens.muestr import muestrear_paráms

métodos = ['morris', 'fast']


class Test_Muestrear(unittest.TestCase):

    def test_muestrear_paráms_sin_mapa_paráms(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        for m in métodos:
            with símismo.subTest(método=m):
                mstr = muestrear_paráms(
                    líms_paráms=líms_paráms,
                    método=m
                )
                for p, l in líms_paráms.items():
                    símismo.assertLessEqual(mstr[p].max(), l[1])
                    símismo.assertGreaterEqual(mstr[p].min(), l[0])

    def test_muestrear_paráms_con_mapa_matr(símismo):
        líms_paráms = {'A': [(0, 1), (2, 3)]}

        mapa_paráms = {'A': [0, 0, 0, 1, 1, 1]}
        for m in métodos:
            with símismo.subTest(método=m):
                mstr = muestrear_paráms(
                    líms_paráms=líms_paráms,
                    mapa_paráms=mapa_paráms,
                    método=m
                )
                símismo.assertEqual(len(mstr), 2)
                for r, mtrz_mstr in zip(líms_paráms['A'], mstr.values()):
                    símismo.assertLessEqual(mtrz_mstr.max(), r[1])
                    símismo.assertGreaterEqual(mtrz_mstr.min(), r[0])

    def test_muestrear_paráms_con_mapa_dic(símismo):
        líms_paráms = {'A': [(0, 1), (2, 3), (4, 5), (6, 7)]}

        mapa_paráms = {
            'A': {
                'transf': 'prom',
                'mapa': {
                    'B': [(0, 1), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)],
                    'C': [(0, 3), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)],
                    'D': [(0, 0), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)]
                }
            }
        }

        for m in métodos:
            with símismo.subTest(método=m):
                mstr = muestrear_paráms(
                    líms_paráms=líms_paráms,
                    mapa_paráms=mapa_paráms,
                    método=m
                )
                símismo.assertEqual(len(mstr), len(líms_paráms['A']))
                for r, mtrz_mstr in zip(líms_paráms['A'], mstr.values()):
                    símismo.assertLessEqual(mtrz_mstr.max(), r[1])
                    símismo.assertGreaterEqual(mtrz_mstr.min(), r[0])

    def test_guardar_mstr_paráms(self):
        pass

    def test_cargar_mstr_paráms(self):
        pass


class test_Corridas(unittest.TestCase):
    def test_gen_vals_inic_con_mapa_matr(símismo):
        líms_paráms = {'A': [(0, 1), (2, 3)]}
        mapa_paráms = {'A': [0, 0, 0, 1, 1, 1]}
        mstr = muestrear_paráms(
            líms_paráms=líms_paráms,
            mapa_paráms=mapa_paráms,
            método='morris'
        )

        vals_inic = gen_vals_inic(mstr=mstr, mapa_paráms=mapa_paráms)  # type: dict[int, dict[str, np.ndarray | int | float]]

        for í, d_í in vals_inic.items():
            símismo.assertEqual(d_í['A'].shape, (6,))
            for p, v in d_í.items():
                mín = np.array(líms_paráms[p])[mapa_paráms[p]][:, 0]
                máx = np.array(líms_paráms[p])[mapa_paráms[p]][:, 1]
                símismo.assertTrue(np.all(np.less_equal(mín, v)) and np.all(np.greater_equal(máx, v)))

    def test_gen_vals_inic_con_mapa_dic(símismo):
        líms_paráms = {'A': [(0, 1), (2, 3), (4, 5), (6, 7)]}
        mapa_paráms = {
            'A': {
                'transf': 'prom',
                'mapa': {
                    'B': [(0, 1), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)],
                    'C': [(0, 3), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)],
                    'D': [(0, 0), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)]
                }
            }
        }
        mstr = muestrear_paráms(
            líms_paráms=líms_paráms,
            mapa_paráms=mapa_paráms,
            método='morris'
        )
        vals_inic = gen_vals_inic(mstr=mstr, mapa_paráms=mapa_paráms)

        for í, d_í in vals_inic.items():
            for var, mapa in mapa_paráms['A']['mapa'].items():
                val_correcto = np.array(
                    [(mstr['A_{}'.format(t_índ[0])][í] + mstr['A_{}'.format(t_índ[1])][í]) / 2 for t_índ in mapa]
                )

                npt.assert_array_equal(val_correcto, d_í[var])
