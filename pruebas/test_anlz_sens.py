import os
import shutil
import unittest
from collections import Counter

import numpy.testing as npt

from pruebas.recursos.BF.prueba_forma import ModeloLinear, ModeloExpo, ModeloLogistic, ModeloInverso, ModeloLog, \
    ModeloOscil, ModeloOscilAten, ModForma
from pruebas.recursos.mod_prueba_sens import ModeloPrueba
from tinamit.Análisis.Sens.anlzr import anlzr_sens, format_simul, gen_bf_simul
from tinamit.Análisis.Sens.behavior import *
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

    def _verificar_sens_mod(
            símismo, mod, t_final, líms_paráms, tipo_egr, sensibles, no_sensibles=None, mtds=None, ops_método=None
    ):
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
            n = 3
            mapa, líms = símismo._gen_mapa_prms(líms_paráms, n, tipo='matr')
            símismo._verif_sens(mod=mod(dims=(n,)), mapa_paráms=mapa, ops_método=ops_método, líms_paráms=líms,
                                t_final=t_final, vars_egr=vars_egr, tipo_egr=tipo_egr,
                                sensibles=sensibles, no_sensibles=no_sensibles, mtds=mtds, ficticia=True)

        with símismo.subTest(tipo_mod='mapa_dic'):
            # raise NotImplementedError
            n = 5
            mapa, líms = símismo._gen_mapa_prms(líms_paráms, n, tipo='dic')
            símismo._verif_sens(mod=mod(dims=(n,)), mapa_paráms=mapa, ops_método=ops_método, líms_paráms=líms,
                                t_final=t_final, vars_egr=vars_egr, tipo_egr=tipo_egr,
                                sensibles=sensibles, no_sensibles=no_sensibles, mtds=mtds, ficticia=True)

    def _gen_matr_i_sens(símismo, líms_prm, mapa_prm, t_final, tipo_egr):
        if not isinstance(mapa_prm, dict):
            if tipo_egr == 'paso_tiempo':
                matr_i_sens = np.zeros([len(líms_prm), t_final + 1, len(mapa_prm)])
                for t in range(t_final + 1):
                    for y in range(len(mapa_prm)):
                        matr_i_sens[mapa_prm[y], t, y] = 1
            else:
                matr_i_sens = np.zeros([len(líms_prm), len(mapa_prm)])
                for y in range(len(mapa_prm)):
                    matr_i_sens[mapa_prm[y], y] = 1
        else:
            l_y = list(mapa_prm['mapa'].values())[0]
            if tipo_egr == 'paso_tiempo':
                matr_i_sens = np.zeros([len(líms_prm), t_final + 1, len(l_y)])
                for t in range(t_final + 1):
                    for y in range(len(l_y)):
                        matr_i_sens[l_y[y], t, y] = 1
            else:
                matr_i_sens = np.zeros([len(líms_prm), len(l_y)])
                for y in range(len(l_y)):
                    if isinstance(l_y[0], tuple):
                        matr_i_sens[l_y[y], y] = 1
                    else:
                        matr_i_sens[mapa_prm[y], y] = 1

        msk = np.greater(matr_i_sens, 0)

        return msk

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
                dims_y = mod.obt_dims_var('y')

                for prm, l_eg in sensibles.items():
                    if mapa_paráms is None or prm not in mapa_paráms:
                        if tipo_egr != 'paso_tiempo':
                            dims_p = (1,)
                        else:
                            if dims_y == (1,):
                                dims_p = (1,)
                            else:
                                dims_p = (t_final + 1,)
                        for eg in l_eg:
                            símismo._proc_res_sens(eg, prm, res, m, tipo_egr, dims_p, dims_y, t_final, mapa_paráms,
                                                   sens=True, i_sens=None)
                    else:
                        mask = símismo._gen_matr_i_sens(líms_paráms[prm], mapa_paráms[prm], t_final, tipo_egr)
                        dims_p = (len(líms_paráms[prm]),)
                        for eg in l_eg:
                            símismo._proc_res_sens(
                                eg, prm, res, m, tipo_egr, dims_p, dims_y, t_final, mapa_paráms, sens=True, i_sens=mask
                            )

                for prm, l_eg in no_sensibles.items():
                    if mapa_paráms is None or prm not in mapa_paráms:
                        if prm == 'Ficticia':
                            continue
                        if tipo_egr != 'paso_tiempo':
                            dims_p = (1,)
                        else:
                            if dims_y == (1,):
                                dims_p = (1,)
                            else:
                                dims_p = (t_final + 1,)

                        for eg in l_eg:
                            símismo._proc_res_sens(eg, prm, res, m, tipo_egr, dims_p, dims_y, t_final,
                                                   mapa_paráms, sens=False, i_sens=None)
                    else:
                        mask = símismo._gen_matr_i_sens(líms_paráms[prm], mapa_paráms[prm], t_final, tipo_egr)
                        dims_p = (len(líms_paráms[prm]),)
                        for eg in l_eg:
                            símismo._proc_res_sens(eg, prm, res, m, tipo_egr, dims_p, dims_y, t_final,
                                                   mapa_paráms, sens=False, i_sens=mask)

    @staticmethod
    def _proc_res_sens(eg, prm, res, m, t_egr, dims_p, dims_y, t_final, mapa_paráms, sens, i_sens):
        if not isinstance(eg, list):
            eg = [eg]

        def _sacar_val(nombre, egr, dims_p, dims_y):
            d_vals = res[t_egr][egr[0]][nombre]
            val_prm = d_vals[prm]
            val_fict = d_vals['Ficticia']

            if egr[1:]:
                for e in egr[1:]:
                    val_prm = val_prm[e]
                    val_fict = val_fict[e]
                _verif_forma(val_prm, dims_p, dims_y)
                return val_prm, val_fict

            else:
                _verif_forma(val_prm, dims_p, dims_y)
                return val_prm, val_fict

        def _verif_forma(val_prm, dims_p, dims_y):
            if mapa_paráms is None:
                if list(res.keys())[0] != 'paso_tiempo':
                    if dims_y == (1,):
                        assert isinstance(val_prm, (int, float))
                    else:
                        assert val_prm.shape == (dims_y)
                else:
                    if dims_y == (1,):
                        assert val_prm.shape == (t_final + 1,)
                    else:
                        assert val_prm.shape == (*dims_p, *dims_y)
            else:
                if list(res.keys())[0] != 'paso_tiempo':
                    assert val_prm.shape == (*dims_p, *dims_y)
                else:
                    assert val_prm.shape == (*dims_p, t_final + 1, *dims_y)

        def _verificar_no_sig(val_prm, val_fict, sello, rtol=0.1):
            if i_sens is not None:
                inv_sens = np.invert(i_sens)

                if val_prm.ndim < 3:
                    _no_sig(val_prm[inv_sens], sello, val_fict[np.where(i_sens)[1]], rtol)

                else:
                    for t in range(t_final + 1):
                        _no_sig(val_prm[inv_sens], sello, val_fict[t, np.where(inv_sens)[2]], rtol)
            else:
                if val_prm.ndim < 2:
                    _no_sig(val_prm, sello, val_fict, rtol)
                else:
                    for y in range(dims_y[0]):
                        _no_sig(val_prm[:, y], sello, val_fict[:, y], rtol)

        def _no_sig(val_prm, sello, val_fict, rtol):
            try:
                npt.assert_array_less(val_prm, sello)
            except AssertionError:
                try:
                    npt.assert_array_less(val_prm, val_fict)
                except AssertionError:
                    npt.assert_allclose(val_prm, val_fict, rtol=rtol)

        def _verificar_sig(val_prm, val_fict, sello, rtol=0.1):
            if i_sens is not None:
                if val_prm.ndim < 3:
                    _sig(val_prm[i_sens], sello, val_fict[np.where(i_sens)[1]], rtol)

                else:
                    for t in range(t_final + 1):
                        _sig(val_prm[i_sens], sello, val_fict[t, np.where(i_sens)[2]], rtol)
            else:
                if val_prm.ndim < 2:
                    _sig(val_prm, sello, val_fict, rtol)
                else:
                    for y in range(dims_y[0]):
                        _sig(val_prm[:, y], sello, val_fict[:, y], rtol)

        def _sig(val_prm, sello, val_fict, rtol):
            npt.assert_array_less(sello, val_prm)
            npt.assert_array_less(val_fict, val_prm)
            npt.assert_array_less(rtol, np.abs(val_fict - val_prm) / val_fict)

        if m == 'morris':
            mu_star_prm, mu_star_fict = _sacar_val('mu_star', eg, dims_p, dims_y)

            if sens:
                _verificar_sig(mu_star_prm, mu_star_fict, sello=0.1)

            else:
                _verificar_no_sig(mu_star_prm, mu_star_fict, sello=0.1)

        elif m == 'fast':
            si_prm, si_fict = _sacar_val('Si', eg, dims_p, dims_y)
            st_si_prm, st_si_fict = _sacar_val('St-Si', eg, dims_p, dims_y)

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
                vr: {'transf': 'prom',
                     'mapa': {vr: [
                         (np.random.choice(range(4)), np.random.choice(range(4))) for _ in range(n)
                     ]}} for vr in líms_prms
            }
        else:
            raise ValueError(tipo)

        return mapa, líms

    def test_sens_paso(símismo):
        líms_paráms = {'A': (0.1, 1), 'B': (2, 3)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=5, líms_paráms=líms_paráms, tipo_egr='paso_tiempo',
            sensibles={'A': 'A', 'B': 'B'},
            no_sensibles={'A': 'B', 'B': 'A', 'Ficticia': ['A', 'B']},
            ops_método=ops_métodos
        )

    def test_sens_final(símismo):
        líms_paráms = {'A': (0.1, 1), 'B': (2, 3)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=5, líms_paráms=líms_paráms, tipo_egr='final',
            sensibles={'A': 'A', 'B': 'B'},
            no_sensibles={'A': 'B', 'B': 'A', 'Ficticia': ['A', 'B']},
            ops_método=ops_métodos
        )

    def test_sens_promedio(símismo):

        líms_paráms = {'A': (0.1, 1), 'B': (2, 3)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=5, líms_paráms=líms_paráms, tipo_egr='promedio',
            sensibles={'A': 'A', 'B': 'B'},
            no_sensibles={'A': 'B', 'B': 'A', 'Ficticia': ['A', 'B']},
            ops_método=ops_métodos
        )

    def test_sens_linear(símismo):
        líms_paráms = {'A': (0.1, 2), 'B': (0.1, 1)}
        símismo._verificar_sens_mod(
            ModeloLinear, t_final=20, líms_paráms=líms_paráms, tipo_egr='linear',
            sensibles={'A': [['y', 'slope']], 'B': [['y', 'intercept']]},
            ops_método=ops_métodos
        )

    def test_sens_expo(símismo):
        líms_paráms = {'A': (0.1, 5), 'B': (1.1, 2)}
        símismo._verificar_sens_mod(
            ModeloExpo, t_final=10, líms_paráms=líms_paráms, tipo_egr='exponencial',
            sensibles={'A': [['y', 'y_intercept']], 'B': [['y', 'g_d']]},
            ops_método=ops_métodos
        )

    def test_sens_logistic(símismo):  # muldim Morris
        líms_paráms = {'A': (5, 10), 'B': (0.85, 2), 'C': (3, 5)}
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

    def test_sens_log(símismo):
        líms_paráms = {'A': (0.5, 2), 'B': (2, 5)}
        símismo._verificar_sens_mod(
            ModeloLog, t_final=10, líms_paráms=líms_paráms, tipo_egr='log',
            sensibles={'A': [['y', 'g_d']], 'B': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_oscilación(símismo):
        líms_paráms = {'A': (0.7, 1.0), 'B': (0.6, 1), 'C': (0.7, 1.0)}
        símismo._verificar_sens_mod(
            ModeloOscil, t_final=10, líms_paráms=líms_paráms, tipo_egr='oscilación',
            sensibles={'A': [['y', 'amplitude']], 'B': [['y', 'period']], 'C': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_ocilación_aten(símismo):
        líms_paráms = {'A': (0.25, 0.3), 'B': (0.7, 1), 'C': (0.6, 1), 'D': (0.7, 1.0)}  # 'A'(0.01, 0.3)
        símismo._verificar_sens_mod(
            ModeloOscilAten, t_final=10, líms_paráms=líms_paráms, tipo_egr='oscilación_aten',
            sensibles={'A': [['y', 'g_d']], 'B': [['y', 'amplitude']], 'C': [['y', 'period']], 'D': [['y', 'phi']]},
            ops_método=ops_métodos
        )

    def test_sens_forma(símismo):
        líms_prms = {'A': (3, 3.5), 'B': (3, 3.5), 'P': (0.1, 1)}
        líms = {vr: [lms] * 2 for vr, lms in líms_prms.items()}
        mapa = {vr: np.random.choice(range(2), size=3) for vr in líms_prms}

        mtds = {'morris': {'num_levels': 4, 'grid_jump': 2},
                'fast': {'N': 65}}

        for m, ops in mtds.items():
            ops_método = mtds[m]
            with símismo.subTest(método=m):
                # res = anlzr_sens(
                #     mod=ModForma(dims=(3,)), método=m, líms_paráms=líms, mapa_paráms=mapa,
                #     t_final=10, var_egr='y', ops_método=ops_método, tipo_egr='forma', ficticia=False)

                res = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\\f_simul\\test_egr.npy").tolist()
                msk_a = símismo._gen_matr_i_sens(líms['A'], mapa['A'], t_final=10, tipo_egr='forma')
                msk_b = símismo._gen_matr_i_sens(líms['B'], mapa['B'], t_final=10, tipo_egr='forma')
                msk_p = símismo._gen_matr_i_sens(líms['P'], mapa['P'], t_final=10, tipo_egr='forma')
                for patt, val in res['forma']['y'].items():
                    param_a = val['gof']['mu_star']['A']['aic'][msk_a]
                    param_b = val['gof']['mu_star']['B']['aic'][msk_b]
                    wt = val['gof']['mu_star']['P']['aic'][msk_p]

                    npt.assert_array_less(param_a, 0.1)
                    npt.assert_array_less(param_b, 0.1)
                    npt.assert_array_less(0.1, wt)

    # verificar AIC sensitivo a ‘p’ y no a "a" o "b"
    # Create a model which could is a combined function y = log + oscilation. and the p is a weight param,
    # the output aic should only sensitive to the weight p, the parameter determined the shapes

    def test_sens_superposition(símismo):
        raise NotImplementedError

    def test_sens_trasiciones(símismo):
        raise NotImplementedError

    @classmethod
    def tearDownClass(cls):
        raise NotImplementedError
        _borrar_direcs_egr()


class Test_AdivinarParams(unittest.TestCase):
    x_data = np.arange(1, 10)
    behaviors = {'linear':
                     {'y_datos': linear(np.array([1, 2]), x_data),
                      'y_dat': linear(np.array([1, 2]), np.arange(1, 20)),
                      'set_parmas': np.array([1, 2])},
                 'exponencial':
                     {'y_datos': exponencial(np.array([2, 1.3, 0.1]), x_data),
                      'y_dat': exponencial(np.array([2, 1.3, 0.1]), np.arange(1, 20)),
                      'set_parmas': np.array([2, 1.3, 0.1])},
                 'logístico':
                     {'y_datos': logístico(np.array([5.0, 0.85, 3.0, 0.1]), x_data),
                      'y_dat': logístico(np.array([5, 1, 8, 0.1]), np.arange(1, 20)),
                      'set_parmas': np.array([5.0, 0.85, 3.0, 0.1])},
                 'inverso':
                     {'y_datos': inverso(np.array([3.0, 0.4, 0.1]), x_data),
                      'y_dat': inverso(np.array([3.0, 0.4, 0.1]), np.arange(1, 20)),
                      'set_parmas': np.array([3.0, 0.4, 0.1])},
                 'log':
                     {'y_datos': log(np.array([0.3, 0.1, 0.1]), x_data),
                      'y_dat': log(np.array([3, -0.5, 6]), np.arange(1, 20)),
                      'set_parmas': np.array([0.3, 0.1, 0.1])},
                 'oscilación':
                     {'y_datos': oscilación(np.array([0.7, 0.6, 1.0, 0.1]), x_data),
                      'y_dat': oscilación(np.array([7, 1.6, 0, 0]), np.arange(1, 20)),
                      'set_parmas': np.array([0.7, 0.6, 1.0, 0.1])},
                 'oscilación_aten':
                     {'y_datos': oscilación_aten(np.array([0.1, 0.7, 2, 0.01, 0.1]), x_data),
                      'y_dat': oscilación_aten(np.array([0.1, 0.7, 2, 0.01, 0.1]), np.arange(1, 20)),
                      # 0.1, 1, 2.4, 2, 0.1
                      'set_parmas': np.array([0.1, 0.7, 2, 0.01, 0.1])}}

    def test_adivinarparams(símismo, behaviors=behaviors):
        for tipo_egr in behaviors:
            with símismo.subTest(tipo_egr):
                pred = np.asarray(list(
                    simple_shape(x_data=np.arange(1, 10), y_data=behaviors[tipo_egr]['y_datos'], tipo_egr=tipo_egr)
                    ['bp_params'].values()))

                npt.assert_allclose(pred, behaviors[tipo_egr]['set_parmas'], rtol=0.05)

    def test_FormaÚnica(símismo, behaviors=behaviors):
        for tipo_egr in behaviors:
            with símismo.subTest(tipo_egr):
                best_behav = find_best_behavior(forma(np.arange(1, 20), behaviors[tipo_egr]['y_dat']))

                counted_behaviors = Counter([k for k, v in best_behav])
                fr_estim = list(counted_behaviors.keys())

                símismo.assertEqual(tipo_egr, fr_estim[0])

    def test_Superposición(símismo):
        # use forma model to generate logístico+osci curve

        # Comprobar con forma sin superposición, Check form without superpo

        # Comprobar con forma con superposición, check shap with superpo
        raise NotImplementedError

        # formas = {
        #     'linear':
        #         {'mod': ModeloLinear(),
        #          'líms_paráms': {'A': (0.1, 2), 'B': (0.1, 1)}},
        #     'exponencial':
        #         {'mod': ModeloExpo(),
        #          'líms_paráms': {'A': (0.1, 5), 'B': (1.1, 2)}},
        #     'logístico':
        #         {'mod': ModeloLogistic(),
        #          'líms_paráms': {'A': (5, 10), 'B': (0.85, 2), 'C': (3, 5)}},
        #     'inverso':
        #         {'mod': ModeloInverso(),
        #          'líms_paráms': {'A': (3, 10), 'B': (0.4, 2)}},
        #     'log':
        #         {'mod': ModeloLog(),
        #          'líms_paráms': {'A': (0.5, 2), 'B': (2, 5)}},
        #     'oscilación':
        #         {'mod': ModeloOscil(),
        #          'líms_paráms': {'A': (0.7, 1.0), 'B': (0.6, 1), 'C': (0.7, 1.0)}},
        #     'oscilación_aten':
        #         {'mod': ModeloOscilAten(),
        #          'líms_paráms': {'A': (0.25, 0.3), 'B': (0.7, 1), 'C': (0.6, 1), 'D': (0.7, 1.0)}}}
        #
        # for patt, val in formas.items():