import os
import shutil
import unittest
import numpy as np
import numpy.testing as npt

from pruebas.recursos.mod_prueba_sens import ModeloPrueba
from tinamit.Análisis.Sens.corridas import gen_vals_inic, gen_índices_grupos, simul_sens, simul_sens_por_grupo, \
    buscar_simuls_faltan, simul_faltan
from tinamit.Análisis.Sens.muestr import muestrear_paráms, guardar_mstr_paráms, cargar_mstr_paráms

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

    def test_guardar_cargar_mstr_paráms(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        mstr = muestrear_paráms(
            líms_paráms=líms_paráms,
            método='morris'
        )
        guardar_mstr_paráms(mstr, 'prueba_guardar')
        mstr_leída = cargar_mstr_paráms('prueba_guardar')
        for p, v in mstr.items():
            npt.assert_array_equal(v, mstr_leída[p])
        if os.path.isfile('prueba_guardar.json'):
            os.remove('prueba_guardar.json')

dic_direcs = {
    'algunas_faltan': 'corridas_algunas_faltan',
    'por_índice': 'corridas_sens_por_índice',
    'sens_todas': 'corridas_sens_todas',


}
class Test_Corridas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        for dr in dic_direcs.values():
            if os.path.isdir(dr):
                shutil.rmtree(dr)

        cls.líms_paráms = {'A': [(0, 1), (2, 3)]}
        cls.mapa_paráms = {'A': [0, 0, 0, 1, 1, 1]}
        cls.mstr = muestrear_paráms(
            líms_paráms=cls.líms_paráms,
            mapa_paráms=cls.mapa_paráms,
            método='morris'
        )

        cls.líms_paráms_d = {'A': [(0, 1), (2, 3), (4, 5), (6, 7)]}
        cls.mapa_paráms_d = {
            'A': {
                'transf': 'prom',
                'mapa': {
                    'B': [(0, 1), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)],
                    'C': [(0, 3), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)],
                    'D': [(0, 0), (0, 3), (0, 2), (1, 1), (1, 2), (1, 2)]
                }
            }
        }
        cls.mstr_d = muestrear_paráms(
            líms_paráms=cls.líms_paráms_d,
            mapa_paráms=cls.mapa_paráms_d,
            método='morris'
        )

        cls.mod = ModeloPrueba()

    def test_gen_vals_inic_con_mapa_matr(símismo):

        vals_inic = gen_vals_inic(mstr=símismo.mstr, mapa_paráms=símismo.mapa_paráms)

        for í, d_í in vals_inic.items():
            símismo.assertEqual(d_í['A'].shape, (6,))
            for p, v in d_í.items():
                mín = np.array(símismo.líms_paráms[p])[símismo.mapa_paráms[p]][:, 0]
                máx = np.array(símismo.líms_paráms[p])[símismo.mapa_paráms[p]][:, 1]
                símismo.assertTrue(np.all(np.less_equal(mín, v)) and np.all(np.greater_equal(máx, v)))

    def test_gen_vals_inic_con_mapa_dic(símismo):

        vals_inic = gen_vals_inic(mstr=símismo.mstr_d, mapa_paráms=símismo.mapa_paráms_d)

        for í, d_í in vals_inic.items():
            for var, mapa in símismo.mapa_paráms_d['A']['mapa'].items():
                val_correcto = np.array(
                    [(símismo.mstr_d['A_{}'.format(t_índ[0])][í] + símismo.mstr_d['A_{}'.format(t_índ[1])][í]) / 2
                     for t_índ in mapa]
                )

                npt.assert_array_equal(val_correcto, d_í[var])

    def test_buscar_faltan(símismo):
        direc = dic_direcs['algunas_faltan']

        índs = [3, 4, 5, 6, 11]
        simul_sens(símismo.mod, símismo.mstr, mapa_paráms=símismo.mapa_paráms, t_final=10,
                   guardar=direc, var_egr=['A'], índices_mstrs=índs, paralelo=False)
        faltan = buscar_simuls_faltan(símismo.mstr, direc=direc)

        símismo.assertSetEqual(set(faltan), set(i for i in range(75) if i not in índs))

    def test_correr_simuls_por_índices(símismo):
        direc = dic_direcs['por_índice']
        simul_sens(símismo.mod, símismo.mstr, mapa_paráms=símismo.mapa_paráms, t_final=10,

                   guardar=direc, var_egr=['A'], índices_mstrs=(0, 20), paralelo=False)

        archivos = set([f for f in os.listdir(direc) if os.path.isfile(os.path.join(direc, f))])
        símismo.assertSetEqual(archivos, set([f'{í}.json' for í in range(0, 20)]))

    def test_gen_índices_grupos(símismo):
        índs_grupos = gen_índices_grupos(n_iter=12, tmñ_grupos=5)
        símismo.assertLessEqual(índs_grupos, [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11]])

    def test_correr_por_grupo(símismo):
        direc = dic_direcs['por_índice']
        simul_sens_por_grupo(
            símismo.mod, símismo.mstr, mapa_paráms=símismo.mapa_paráms, t_final=10,
            guardar=direc, var_egr=['A'], tmñ_grupos=5, í_grupos=1, paralelo=False
        )
        archivos = set([f for f in os.listdir(direc) if os.path.isfile(os.path.join(direc, f))])
        símismo.assertSetEqual(archivos, set([f'{í}.json' for í in range(5, 10)]))

    def test_correr_simuls_faltan(símismo):
        direc = dic_direcs['algunas_faltan']
        índs = [3, 4, 5, 6, 11]
        simul_sens(símismo.mod, símismo.mstr, mapa_paráms=símismo.mapa_paráms, t_final=10,
                   guardar=direc, var_egr=['A'], índices_mstrs=índs, paralelo=False)
        guardar_mstr_paráms(símismo.mstr, os.path.join(direc, 'mstr.json'))
        simul_faltan(símismo.mod, os.path.join(direc, 'mstr.json'), mapa_paráms=símismo.mapa_paráms, t_final=10,
                     direc=direc, var_egr=['A'])

        todavía_faltan = buscar_simuls_faltan(mstr=símismo.mstr, direc=direc)
        símismo.assertEqual(len(todavía_faltan), 0)

    def test_correr_todas_simuls(símismo):
        direc = dic_direcs['sens_todas']
        simul_sens(símismo.mod, símismo.mstr, mapa_paráms=símismo.mapa_paráms, t_final=10,

                   guardar=direc, var_egr=['A'], paralelo=False)
        n_iter = len(list(símismo.mstr.values())[0])
        archivos = set([f for f in os.listdir(direc) if os.path.isfile(os.path.join(direc, f))])
        símismo.assertSetEqual(archivos, set([f'{í}.json' for í in range(n_iter)]))

    @classmethod
    def tearDownClass(cls):
        for dr in dic_direcs.values():
            if os.path.isdir(dr):
                shutil.rmtree(dr)


class Test_Análisis(unittest.TestCase):
    pass
