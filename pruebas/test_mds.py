import os
import unittest

from tinamit.EnvolturaMDS import generar_mds, EnvolturaMDS, ModeloVensim, ModeloPySD, ModeloVensimMdl
from tinamit.EnvolturaMDS.Vensim import dll_Vensim


class Test_ModeloSenc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        tipos_modelos = {
            'mdlVensim': {'envlt': ModeloVensimMdl, 'prueba': 'recursos/prueba_senc.mdl'},
            'PySDVensim': {'envlt': ModeloPySD, 'prueba': 'recursos/prueba_senc.mdl'},
            'PySD_XMILE': {'envlt': ModeloPySD, 'prueba': 'recursos/prueba_senc_.xmile'},
            'dllVensim': {'envlt': ModeloVensim, 'prueba': 'recursos/prueba_senc.vpm'}
        }

        for nmb in list(tipos_modelos):
            if not tipos_modelos[nmb]['envlt'].instalado:
                tipos_modelos.pop(nmb)

        cls.modelos = {ll: d['envlt'](d['prueba']) for ll, d in tipos_modelos.items()}  # type: dict[str, EnvolturaMDS]

        cls.info_vars = {
            'Lluvia': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Nivel lago inicial': {'unidades': 'm3', 'líms': (0, None), 'val_inic': 1500},
            'Flujo río': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Evaporación': {'unidades': 'm3/mes', 'líms': (0, None)}
        }

        for mod in cls.modelos.values():
            for v, d_v in cls.info_vars.items():
                if 'val_inic' in d_v:
                    mod.inic_val(v, d_v['val_inic'])

            mod.simular(tiempo_final=200, vars_interés='Lago')

    def test_leer_vars(símismo):
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                vars_modelo = set(mod.variables)
                símismo.assertSetEqual(set(símismo.info_vars), vars_modelo)

    def test_unid_tiempo(símismo):
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertEqual('mes', mod.unidad_tiempo.lower())

    def test_leer_info(símismo):

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertTrue(len(d_v['info']) > 0 for d_v in mod.variables.values())

    def test_leer_unidades(símismo):

        unids = {v: d_v['unidades'] for v, d_v in símismo.info_vars.items()}

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                unids_mod = {v: d_v['unidades'].lower() for v, d_v in mod.variables.items()}
                símismo.assertDictEqual(unids, unids_mod)

    def test_leer_líms(símismo):
        unids = {v: d_v['líms'] for v, d_v in símismo.info_vars.items()}

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                unids_mod = {v: d_v['líms'] for v, d_v in mod.variables.items()}
                símismo.assertDictEqual(unids, unids_mod)

    def test_cmb_vals_inic(símismo):
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertEqual(mod.variables['Nivel lago inicial']['val'], 1500)

    def test_simul(símismo):
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                val_simulado = mod.leer_resultados('Lago')[-1, 0]
                símismo.assertEqual(round(val_simulado, 3), 100)

    @classmethod
    def tearDownClass(cls):
        for c in os.walk('../recursos'):
            for a in c[2]:
                nmbr, ext = os.path.splitext(a)
                try:
                    if nmbr == 'Corrida Tinamït':
                        os.remove(a)
                    elif ext in ['.2mdl', '.vdf']:
                        os.remove(a)
                    elif a == 'prueba_senc.py':
                        os.remove(a)
                    elif a == 'prueba_senc_.py':
                        os.remove(a)
                except PermissionError:
                    pass
