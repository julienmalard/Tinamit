import os
import shutil
import unittest

import numpy as np
import numpy.testing as npt

from pruebas.recursos.BF.prueba_forma import ModeloLinear, ModeloExpo, ModeloLogistic, ModeloInverso, ModeloLog, \
    ModeloOscil, ModeloOscilAten
from pruebas.recursos.mod_prueba_sens import ModeloPrueba
from tinamit.Análisis.Sens.anlzr import anlzr_sens
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


def _borrar_direcs_egr():
    for dr in dic_direcs.values():
        if os.path.isdir(dr):
            shutil.rmtree(dr)


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
        _borrar_direcs_egr()


ops_métodos = {'morris': {'num_levels': 4, 'grid_jump': 2}}


class Test_Análisis(unittest.TestCase):

    def _verificar_sens_mod(símismo, mod, t_final, líms_paráms, tipo_egr, sensibles, no_sensibles=None, mtds=None,
                            ops_método=None):
        if mtds is None:
            mtds = métodos
        if ops_método is None:
            ops_método = {}

        if sensibles is None:
            sensibles = {}
        else:
            for prm, vr in sensibles.items():
                if isinstance(vr, str):
                    sensibles[prm] = [vr]

        vars_egr = []
        for prm, l_vr in sensibles.items():
            for vr in l_vr:
                if isinstance(vr, list):
                    vars_egr.append(vr[0])
                else:
                    vars_egr.append(vr)

        if no_sensibles is None:
            no_sensibles = {
                prm: [vr[0] for otro_prm, vr in sensibles.items() if otro_prm != prm] for prm in sensibles
            }
        else:
            for prm, l_vr in no_sensibles.items():
                for vr in l_vr:
                    if isinstance(vr, list):
                        vars_egr.append(vr[0])
                    else:
                        vars_egr.append(vr)

        vars_egr = list(set(vars_egr))

        with símismo.subTest(tipo_mod='sencillo'):
            símismo._verif_sens(mod=mod(), mapa_paráms=None, ops_método=ops_método, líms_paráms=líms_paráms,
                                t_final=t_final, vars_egr=vars_egr, tipo_egr=tipo_egr,
                                sensibles=sensibles, no_sensibles=no_sensibles, mtds=mtds, ficticia=True)

        with símismo.subTest(tipo_mod='multidim'):
            símismo._verif_sens(mod=mod(dims=(3,)), mapa_paráms=None, ops_método=ops_método, líms_paráms=líms_paráms,
                                t_final=t_final, vars_egr=vars_egr, tipo_egr=tipo_egr,
                                sensibles=sensibles, no_sensibles=no_sensibles, mtds=mtds, ficticia=True)

        with símismo.subTest(tipo_mod='mapa_matr'):
            raise NotImplementedError
            n = 3
            mapa, líms = símismo._gen_mapa_prms(líms_paráms, n, tipo='matr')
            símismo._verif_sens(mod=mod(dims=(n,)), mapa_paráms=mapa, ops_método=ops_método, líms_paráms=líms,
                                t_final=t_final, vars_egr=vars_egr, tipo_egr=tipo_egr,
                                sensibles=sensibles, no_sensibles=no_sensibles, mtds=mtds, ficticia=True)

        with símismo.subTest(tipo_mod='mapa_dic'):
            raise NotImplementedError
            n = 10
            mapa, líms = símismo._gen_mapa_prms(líms_paráms, n, tipo='dic')
            símismo._verif_sens(mod=mod(dims=(n,)), mapa_paráms=mapa, ops_método=ops_método, líms_paráms=líms,
                                t_final=t_final, vars_egr=vars_egr, tipo_egr=tipo_egr,
                                sensibles=sensibles, no_sensibles=no_sensibles, mtds=mtds, ficticia=True)

    def _verif_sens(
            símismo, mod, mapa_paráms, ops_método, líms_paráms, t_final, vars_egr, tipo_egr,
            sensibles, no_sensibles, mtds, ficticia
    ):
        for m in mtds:
            if m not in ops_método:
                ops_método[m] = {}

            with símismo.subTest(método=m):
                res = anlzr_sens(
                    mod, método=m, mapa_paráms=mapa_paráms, líms_paráms=líms_paráms,
                    t_final=t_final, var_egr=vars_egr, ops_método=ops_método[m], tipo_egr=tipo_egr, ficticia=ficticia
                )
                if mapa_paráms is None:
                    for prm, l_eg in sensibles.items():
                        for eg in l_eg:
                            símismo._proc_res_sens(eg, prm, res, m, tipo_egr, sens=True)
                    for prm, l_eg in no_sensibles.items():
                        for eg in l_eg:
                            símismo._proc_res_sens(eg, prm, res, m, tipo_egr, sens=False)
                else:
                    raise NotImplementedError

    @staticmethod
    def _proc_res_sens(eg, prm, res, m, t_egr, sens):
        if not isinstance(eg, list):
            eg = [eg]

        def _sacar_val(nombre, egr):
            d_vals = res[t_egr][egr[0]][nombre]
            val_prm = d_vals[prm]
            val_fict = d_vals['Ficticia']

            for e in egr[1:]:
                val_prm = val_prm[e]
                val_fict = val_fict[e]

            return val_prm, val_fict

        def _verificar_no_sig(val_prm, val_fict, sello, rtol=0.5):
            try:
                npt.assert_array_less(val_prm, sello)
            except AssertionError:
                try:
                    npt.assert_array_less(val_prm, val_fict)
                except AssertionError:
                    npt.assert_allclose(val_prm, val_fict, rtol=rtol, atol=0.5)

        def _verificar_sig(val_prm, val_fict, sello, rtol=0.5):
            npt.assert_array_less(sello, val_prm)
            npt.assert_array_less(val_fict, val_prm)
            npt.assert_array_less(rtol, np.abs(val_fict - val_prm) / val_fict)

        if m == 'morris':
            pass
            mu_star_prm, mu_star_fict = _sacar_val('mu_star', eg)

            if sens:
                _verificar_sig(mu_star_prm, mu_star_fict, sello=0.1)

            else:
                _verificar_no_sig(mu_star_prm, mu_star_fict, sello=0.1)

        elif m == 'fast':
            si_prm, si_fict = _sacar_val('Si', eg)
            st_si_prm, st_si_fict = _sacar_val('St-Si', eg)

            if sens:
                _verificar_sig(si_prm, si_fict, sello=0.01)
            else:
                _verificar_no_sig(st_si_prm, st_si_fict, sello=0.1)
                _verificar_no_sig(si_prm, si_fict, sello=0.01)

        else:
            raise ValueError(m)

    @staticmethod
    def _gen_mapa_prms(líms_prms, n, tipo):

        if tipo == 'matr':
            líms = {vr: [lms] * 2 for vr, lms in líms_prms.items()}
            mapa = {vr: np.random.choice(range(2), size=n) for vr in líms_prms}

        elif tipo == 'dic':
            líms = {vr: [lms] * 4 for vr, lms in líms_prms.items()}
            mapa = {
                'transf': 'prom',
                'mapa': {vr: [
                    (np.random.choice(range(4)), np.random.choice(range(4))) for _ in range(n)
                ] for vr in líms_prms}
            }
        else:
            raise ValueError(tipo)

        return mapa, líms

    def test_sens_paso(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=5, líms_paráms=líms_paráms, tipo_egr='paso_tiempo',
            sensibles={'A': 'A', 'B': 'B'},
            no_sensibles={'A': 'B', 'B': 'A', 'Ficticia': ['A', 'B']},
            ops_método=ops_métodos
        )

    def test_sens_final(símismo):
        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=5, líms_paráms=líms_paráms, tipo_egr='final',
            sensibles={'A': 'A', 'B': 'B'},
            no_sensibles={'A': 'B', 'B': 'A', 'Ficticia': ['A', 'B']},
            ops_método=ops_métodos
        )

    def test_sens_promedio(símismo):

        líms_paráms = {'A': (0, 1), 'B': (2, 3)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=5, líms_paráms=líms_paráms, tipo_egr='promedio',
            sensibles={'A': 'A', 'B': 'B'},
            no_sensibles={'A': 'B', 'B': 'A', 'Ficticia': ['A', 'B']},
            ops_método=ops_métodos
        )

    def test_sens_linear(símismo):
        líms_paráms = {'A': (0, 2), 'B': (0, 1)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=20, líms_paráms=líms_paráms, tipo_egr='linear',
            sensibles={'A': [['y', 'slope']], 'B': [['y', 'intercept']]},
            ops_método=ops_métodos
        )

    def test_sens_expo(símismo):
        líms_paráms = {'A': (0.1, 5), 'B': (1.1, 2)}
        símismo._verificar_sens_mod(
            ModeloExpo, t_final=15, líms_paráms=líms_paráms, tipo_egr='exponencial',
            sensibles={'A': [['y', 'y_intercept']], 'B': [['y', 'g_d']]},
            ops_método=ops_métodos
        )

    def test_sens_logistic(símismo): # muldim Morris
        líms_paráms = {'A': (5, 10), 'B': (0.85, 2), 'C': (3, 5)} #C (2, 3)
        símismo._verificar_sens_mod(
            ModeloLogistic, t_final=10, líms_paráms=líms_paráms, tipo_egr='logístico',
            sensibles={'A': [['y', 'maxi_val']], 'B': [['y', 'g_d']], 'C': [['y', 'mid_point']]},
            ops_método=ops_métodos
        )

    def test_sens_inverse(símismo):
        líms_paráms = {'A': (3, 10), 'B': (0.4, 2)}
        símismo._verificar_sens_mod(
            ModeloInverso, t_final=10, líms_paráms=líms_paráms, tipo_egr='inverso',
            sensibles={'A': [['y', 'g_d']], 'B': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_log(símismo): # multidim not working, or Morris_multidim
        líms_paráms = {'A': (0.5, 2), 'B': (2, 5)}
        símismo._verificar_sens_mod(
            ModeloLog, t_final=10, líms_paráms=líms_paráms, tipo_egr='log',
            sensibles={'A': [['y', 'g_d']], 'B': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_oscilación(símismo): # not stable... simple Morris crush sometimes
        líms_paráms = {'A': (0.7, 1.0), 'B': (0.6, 0.8), 'C': (1.1, 1.4)}
        símismo._verificar_sens_mod(
            ModeloOscil, t_final=20, líms_paráms=líms_paráms, tipo_egr='oscilación',
            sensibles={'A': [['y', 'amplitude']], 'B': [['y', 'period']], 'C': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_ocilación_aten(símismo): # no
        líms_paráms = {'A': (0.01, 0.2), 'B': (0.7, 1), 'C': (0.6, 0.8), 'D': (1.1, 1.4)} #'A'(0.01, 0.3)
        símismo._verificar_sens_mod(
            ModeloOscilAten, t_final=10, líms_paráms=líms_paráms, tipo_egr='oscilación_aten',
            sensibles={'A': [['y', 'g_d']], 'B': [['y', 'amplitude']], 'C': [['y', 'period']], 'D': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_forma(símismo):
        raise NotImplementedError

    def test_sens_trasiciones(símismo):
        raise NotImplementedError

    def test_ficticia_análisis_sens(símismo):
        raise NotImplementedError

    @classmethod
    def tearDownClass(cls):
        _borrar_direcs_egr()
