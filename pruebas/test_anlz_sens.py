import os
import shutil
import unittest
import numpy as np
import numpy.testing as npt

from pruebas.recursos.BF.prueba_forma import ModeloLinear, ModeloExpo, ModeloLogistic
from pruebas.recursos.mod_prueba_sens import ModeloPrueba
from tinamit.Análisis.Sens.corridas import gen_vals_inic, gen_índices_grupos, simul_sens, simul_sens_por_grupo, \
    buscar_simuls_faltan, simul_faltan
from tinamit.Análisis.Sens.muestr import muestrear_paráms, guardar_mstr_paráms, cargar_mstr_paráms, gen_problema
from tinamit.Análisis.Sens.anlzr import anlzr_sens
from SALib.analyze import morris, fast

métodos = ['morris', 'fast']


class Test_Muestrear(unittest.TestCase):

    def test_muestrear_paráms_sin_mapa_paráms(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        for m in métodos:
            with símismo.subTest(método=m):
                mstr = muestrear_paráms(
                    líms_paráms=líms_paráms,
                    método=m, ficticia=False
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
                    método=m, ficticia=False
                )
                símismo.assertEqual(len(mstr), 3)
                mstr = [j for i, j in enumerate(mstr.values()) if i != 0]
                for r, mtrz_mstr in zip(líms_paráms['A'], mstr):
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
                    método=m, ficticia=False
                )
                símismo.assertEqual(len(mstr) - 1, len(líms_paráms['A']))
                mstr = [j for i, j in enumerate(mstr.values()) if i != 0]
                for r, mtrz_mstr in zip(líms_paráms['A'], mstr):
                    símismo.assertLessEqual(mtrz_mstr.max(), r[1])
                    símismo.assertGreaterEqual(mtrz_mstr.min(), r[0])

    def test_guardar_cargar_mstr_paráms(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        mstr = muestrear_paráms(
            líms_paráms=líms_paráms,
            método='morris', ficticia=False
        )
        guardar_mstr_paráms(mstr, 'prueba_guardar')
        mstr_leída = cargar_mstr_paráms('prueba_guardar')
        for p, v in mstr.items():
            npt.assert_array_equal(v, mstr_leída[p])
        if os.path.isfile('prueba_guardar.json'):
            os.remove('prueba_guardar.json')

    def test_ficticia_samples(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        for m in métodos:
            with símismo.subTest(método=m):
                mstr = muestrear_paráms(
                    líms_paráms=líms_paráms,
                    método=m,
                    ficticia=True
                )
                símismo.assertLessEqual(mstr['Ficticia'].max(), 1)
                símismo.assertGreaterEqual(mstr['Ficticia'].min(), 0)


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
            método='morris', ficticia=False
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
            método='morris', ficticia=False
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

        símismo.assertSetEqual(set(faltan), set(i for i in range(100) if i not in índs))

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

    def test_ficticia_ignore_in_value_inic(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        for m in métodos:
            with símismo.subTest(método=m):
                mstr = muestrear_paráms(
                    líms_paráms=líms_paráms,
                    método=m,
                    ficticia=True
                )
                simul_sens(símismo.mod, mstr_paráms=mstr, mapa_paráms=None, t_final=5, var_egr='A')

    @classmethod
    def tearDownClass(cls):
        for dr in dic_direcs.values():
            if os.path.isdir(dr):
                shutil.rmtree(dr)


dic_direcs2 = {
    'algunas_faltan': 'corridas_algunas_faltan',
    'por_índice': 'corridas_sens_por_índice',
    'sens_todas': 'corridas_sens_todas',
}


class Test_Análisis(unittest.TestCase):

    def test_sens_paso(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        mod = ModeloLinear()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['A', 'B'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="paso_tiempo")

                    npt.assert_array_less(0.1, np.asarray(res['paso_tiempo']['A']['mu_star']['A']))
                    npt.assert_array_less(np.asarray(res['paso_tiempo']['A']['mu_star']['B']), 0.1)
                    npt.assert_array_less(np.asarray(res['paso_tiempo']['A']['mu_star']['Ficticia']), 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=3, var_egr=['A', 'B'],
                                     tipo_egr="paso_tiempo")
                    npt.assert_array_less(0.01, np.asarray(res['paso_tiempo']['A']['Si']['A']))
                    símismo.assertTrue(res['paso_tiempo']['A']['Si']['B'] < 0.01 and
                                       res['paso_tiempo']['A']['St-Si']['B'] < 0.1)
                    símismo.assertTrue(res['paso_tiempo']['A']['Si']['Ficticia'] < 0.01 and
                                       res['paso_tiempo']['A']['St-Si']['Ficticia'] < 0.1)
            else:
                raise NotImplementedError

    def test_sens_final(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        mod = ModeloLinear()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['A', 'B'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="final")

                    símismo.assertGreaterEqual(res['final']['A']['mu_star']['A'], 0.1)
                    símismo.assertLessEqual(res['final']['A']['mu_star']['B'], 0.1)
                    símismo.assertLessEqual(res['final']['A']['mu_star']['Ficticia'], 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=3, var_egr=['A', 'B'],
                                     tipo_egr="final")
                    símismo.assertGreaterEqual(res['final']['A']['Si']['A'], 0.01)
                    símismo.assertTrue(res['final']['A']['Si']['B'] < 0.01 and res['final']['A']['St-Si']['B'] < 0.1)
                    símismo.assertTrue(res['final']['A']['Si']['Ficticia'] < 0.01 and
                                       res['final']['A']['St-Si']['Ficticia'] < 0.1)
            else:
                raise NotImplementedError

    def test_sens_promedio(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        mod = ModeloLinear()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['A', 'B'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="promedio")

                    símismo.assertGreaterEqual(res['promedio']['A']['mu_star']['A'], 0.1)
                    símismo.assertLessEqual(res['promedio']['A']['mu_star']['B'], 0.1)
                    símismo.assertLessEqual(res['promedio']['A']['mu_star']['Ficticia'], 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=3, var_egr=['A', 'B'],
                                     tipo_egr="promedio")
                    símismo.assertGreaterEqual(res['promedio']['A']['Si']['A'], 0.01)
                    símismo.assertTrue(res['promedio']['A']['Si']['B'] < 0.01 and
                                       res['promedio']['A']['St-Si']['B'] < 0.1)
                    símismo.assertTrue(res['promedio']['A']['Si']['Ficticia'] < 0.01 and
                                       res['promedio']['A']['St-Si']['Ficticia'] < 0.1)
            else:
                raise NotImplementedError

    def test_sens_linear(símismo):
        líms_paráms = {'A': (0, 2), 'B': (0, 1)}
        mod = ModeloLinear()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="linear")

                    mu_star = res['linear']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['slope'], 0.1)
                    npt.assert_allclose(mu_star['A']['intercept'], mu_star['Ficticia']['intercept'], rtol=0.5)

                    símismo.assertGreaterEqual(mu_star['B']['intercept'], 0.1)
                    npt.assert_allclose(mu_star['B']['slope'], mu_star['Ficticia']['slope'], rtol=0.5)


            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     tipo_egr="linear")

                    si = res['linear']['y']['Si']
                    st_si = res['linear']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['slope'], 0.01)
                    símismo.assertTrue(si['A']['intercept'] <= 0.01 and st_si['A']['intercept'] <= 0.1)

                    símismo.assertGreaterEqual(si['B']['intercept'], 0.01)
                    símismo.assertTrue(si['B']['slope'] <= 0.01 and st_si['B']['slope'] <= 0.1)

                    símismo.assertTrue(si['Ficticia']['intercept'] <= 0.01 and st_si['Ficticia']['intercept'] <= 0.1)
                    símismo.assertTrue(si['Ficticia']['slope'] <= 0.01 and st_si['Ficticia']['slope'] <= 0.1)
            else:
                raise NotImplementedError

    def test_sens_expo(símismo):
        líms_paráms = {'A': (0.0000001, 10), 'B': (0.0000001, 2)}
        mod = ModeloExpo()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     ops_método={'num_levels': 4, 'grid_jump': 2}, tipo_egr="exponential")
                    mu_star = res['exponential']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['y_intercept'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['g_d'], 0.1)

                    símismo.assertLessEqual(mu_star['B']['y_intercept'], 0.1)
                    símismo.assertGreaterEqual(mu_star['B']['g_d'], 0.1)

                    símismo.assertLessEqual(mu_star['Ficticia']['y_intercept'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['g_d'], 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     tipo_egr="exponential")
                    si = res['exponential']['y']['Si']
                    st_si = res['exponential']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['y_intercept'], 0.01)
                    símismo.assertTrue(si['A']['g_d'] < 0.01 and st_si['A']['g_d'] < 0.1)

                    símismo.assertGreaterEqual(si['B']['g_d'], 0.01)
                    símismo.assertTrue(si['B']['y_intercept'] < 0.01 and st_si['B']['y_intercept'] < 0.1)

                    símismo.assertTrue(si['Ficticia']['g_d'] < 0.01 and st_si['Ficticia']['g_d'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['y_intercept'] < 0.01 and st_si['Ficticia']['y_intercept'] < 0.1)
            else:
                raise NotImplementedError

    def test_sens_logistic(símismo):
        líms_paráms = {'A': (3, 10), 'B': (0.5, 2), 'C': (3, 5)}
        mod = ModeloLogistic()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="logistic")
                    # should be more sensitive to B than A (B-rate of growth and decay, A Y-intercept)
                    mu_star = res['logistic']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['mid_point'], 0.1)

                    símismo.assertGreaterEqual(mu_star['B']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['B']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['B']['mid_point'], 0.1)

                    símismo.assertLessEqual(mu_star['Ficticia']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['mid_point'], 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=3, var_egr=['y'],
                                     tipo_egr="logistic")

                    si = res['logistic']['y']['Si']
                    st_si = res['logistic']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['maxi_val'], 0.01)
                    símismo.assertTrue(si['A']['g_d'] < 0.01 and st_si['A']['g_d'] < 0.1)
                    símismo.assertTrue(si['A']['mid_point'] < 0.01 and st_si['A']['mid_point'] < 0.1)


                    símismo.assertGreaterEqual(si['B']['g_d'], 0.01)
                    símismo.assertTrue(si['B']['maxi_val'] < 0.01 and st_si['B']['maxi_val'] < 0.1)
                    símismo.assertTrue(si['B']['mid_point'] < 0.01 and st_si['B']['mid_point'] < 0.1)

                    símismo.assertGreaterEqual(si['C']['mid_point'], 0.01)
                    símismo.assertTrue(si['C']['g_d'] < 0.01 and st_si['C']['g_d'] < 0.1)
                    símismo.assertTrue(si['C']['maxi_val'] < 0.01 and st_si['C']['maxi_val'] < 0.1)

                    símismo.assertTrue(si['Ficticia']['maxi_val'] < 0.01 and st_si['Ficticia']['maxi_val'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['g_d'] < 0.01 and st_si['Ficticia']['g_d'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['mid_point'] < 0.01 and st_si['Ficticia']['mid_point'] < 0.1)

            else:
                raise NotImplementedError

    def test_sens_inverse(símismo):
        líms_paráms = {'A': (0.2, 2), 'B': (0.1, 1)}
        mod = ModeloExpo()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     ops_método={'num_levels': 4, 'grid_jump': 2}, tipo_egr="inverse")
                    # b_params = {'g_d': params[0], 'phi': params[1]}
                    mu_star = res['inverse']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['phi'], 0.1)

                    símismo.assertLessEqual(mu_star['B']['phi'], 0.1)
                    símismo.assertGreaterEqual(mu_star['B']['g_d'], 0.1)

                    símismo.assertLessEqual(mu_star['Ficticia']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['phi'], 0.1)

            elif m == 'fast':
                continue
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     tipo_egr="inverse")
                    si = res['inverse']['y']['Si']
                    st_si = res['inverse']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['g_d'], 0.01)
                    símismo.assertTrue(si['A']['phi'] < 0.01 and st_si['A']['phi'] < 0.1)

                    símismo.assertGreaterEqual(si['B']['phi'], 0.01)
                    símismo.assertTrue(si['B']['g_d'] < 0.01 and st_si['B']['g_d'] < 0.1)

                    símismo.assertTrue(si['Ficticia']['g_d'] < 0.01 and st_si['Ficticia']['g_d'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['phi'] < 0.01 and st_si['Ficticia']['phi'] < 0.1)
            else:
                raise NotImplementedError

    def test_sens_log(símismo):
        líms_paráms = {'A': (0.2, 2), 'B': (0.1, 1)}
        mod = ModeloExpo()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     ops_método={'num_levels': 4, 'grid_jump': 2}, tipo_egr="log")
                    # b_params = {'g_d': params[0], 'phi': params[1]}
                    mu_star = res['log']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['phi'], 0.1)

                    símismo.assertLessEqual(mu_star['B']['phi'], 0.1)
                    símismo.assertGreaterEqual(mu_star['B']['g_d'], 0.1)

                    símismo.assertLessEqual(mu_star['Ficticia']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['phi'], 0.1)

            elif m == 'fast':
                continue
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'],
                                     tipo_egr="log")
                    si = res['log']['y']['Si']
                    st_si = res['log']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['g_d'], 0.01)
                    símismo.assertTrue(si['A']['phi'] < 0.01 and st_si['A']['phi'] < 0.1)

                    símismo.assertGreaterEqual(si['B']['phi'], 0.01)
                    símismo.assertTrue(si['B']['g_d'] < 0.01 and st_si['B']['g_d'] < 0.1)

                    símismo.assertTrue(si['Ficticia']['g_d'] < 0.01 and st_si['Ficticia']['g_d'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['phi'] < 0.01 and st_si['Ficticia']['phi'] < 0.1)
            else:
                raise NotImplementedError

    def test_sens_ocilación(símismo):
        líms_paráms = {'A': (3, 10), 'B': (0.5, 2), 'C': (3, 5)}
        mod = ModeloLogistic()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    continue
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="ocilación")
                    # b_params = {'amplitude': params[0], 'period': params[1], 'phi': params[2]}
                    # should be more sensitive to B than A (B-rate of growth and decay, A Y-intercept)
                    mu_star = res['ocilación']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['mid_point'], 0.1)

                    símismo.assertGreaterEqual(mu_star['B']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['B']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['B']['mid_point'], 0.1)

                    símismo.assertLessEqual(mu_star['Ficticia']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['mid_point'], 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=3, var_egr=['y'],
                                     tipo_egr="ocilación")

                    si = res['ocilación']['y']['Si']
                    st_si = res['logistic']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['maxi_val'], 0.01)
                    símismo.assertTrue(si['A']['g_d'] < 0.01 and st_si['A']['g_d'] < 0.1)
                    símismo.assertTrue(si['A']['mid_point'] < 0.01 and st_si['A']['mid_point'] < 0.1)

                    símismo.assertGreaterEqual(si['B']['g_d'], 0.01)
                    símismo.assertTrue(si['B']['maxi_val'] < 0.01 and st_si['B']['maxi_val'] < 0.1)
                    símismo.assertTrue(si['B']['mid_point'] < 0.01 and st_si['B']['mid_point'] < 0.1)

                    símismo.assertGreaterEqual(si['C']['mid_point'], 0.01)
                    símismo.assertTrue(si['C']['g_d'] < 0.01 and st_si['C']['g_d'] < 0.1)
                    símismo.assertTrue(si['C']['maxi_val'] < 0.01 and st_si['C']['maxi_val'] < 0.1)

                    símismo.assertTrue(si['Ficticia']['maxi_val'] < 0.01 and st_si['Ficticia']['maxi_val'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['g_d'] < 0.01 and st_si['Ficticia']['g_d'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['mid_point'] < 0.01 and st_si['Ficticia']['mid_point'] < 0.1)

            else:
                raise NotImplementedError

    def test_sens_ocilación_aten(símismo):
        líms_paráms = {'A': (3, 10), 'B': (0.5, 2), 'C': (3, 5)}
        mod = ModeloLogistic()
        for m in métodos:
            if m == 'morris':
                with símismo.subTest(método='morris'):
                    continue
                    res = anlzr_sens(mod, método=m, num_samples=100, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=5, var_egr=['y'], ops_método={'num_levels': 4, 'grid_jump': 2},
                                     tipo_egr="ocilación_aten")
                    # b_params = {'g_d': params[0], 'amplitude': params[1], 'period': params[2], 'phi': params[3]}
                    # should be more sensitive to B than A (B-rate of growth and decay, A Y-intercept)
                    mu_star = res['ocilación_aten']['y']['mu_star']
                    símismo.assertGreaterEqual(mu_star['A']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['A']['mid_point'], 0.1)

                    símismo.assertGreaterEqual(mu_star['B']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['B']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['B']['mid_point'], 0.1)

                    símismo.assertLessEqual(mu_star['Ficticia']['maxi_val'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['g_d'], 0.1)
                    símismo.assertLessEqual(mu_star['Ficticia']['mid_point'], 0.1)

            elif m == 'fast':
                with símismo.subTest(método='fast'):
                    res = anlzr_sens(mod, método='fast', num_samples=195, mapa_paráms=None, líms_paráms=líms_paráms,
                                     t_final=3, var_egr=['y'],
                                     tipo_egr="ocilación_aten")

                    si = res['ocilación_aten']['y']['Si']
                    st_si = res['ocilación_aten']['y']['St-Si']
                    símismo.assertGreaterEqual(si['A']['maxi_val'], 0.01)
                    símismo.assertTrue(si['A']['g_d'] < 0.01 and st_si['A']['g_d'] < 0.1)
                    símismo.assertTrue(si['A']['mid_point'] < 0.01 and st_si['A']['mid_point'] < 0.1)

                    símismo.assertGreaterEqual(si['B']['g_d'], 0.01)
                    símismo.assertTrue(si['B']['maxi_val'] < 0.01 and st_si['B']['maxi_val'] < 0.1)
                    símismo.assertTrue(si['B']['mid_point'] < 0.01 and st_si['B']['mid_point'] < 0.1)

                    símismo.assertGreaterEqual(si['C']['mid_point'], 0.01)
                    símismo.assertTrue(si['C']['g_d'] < 0.01 and st_si['C']['g_d'] < 0.1)
                    símismo.assertTrue(si['C']['maxi_val'] < 0.01 and st_si['C']['maxi_val'] < 0.1)

                    símismo.assertTrue(si['Ficticia']['maxi_val'] < 0.01 and st_si['Ficticia']['maxi_val'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['g_d'] < 0.01 and st_si['Ficticia']['g_d'] < 0.1)
                    símismo.assertTrue(si['Ficticia']['mid_point'] < 0.01 and st_si['Ficticia']['mid_point'] < 0.1)

            else:
                raise NotImplementedError


    @unittest.skip
    def test_sens_forma(símismo):
        raise NotImplementedError

    def test_sens_trasiciones(símismo):
        raise NotImplementedError

    def test_ficticia_análisis_sens(símismo):
        raise NotImplementedError
