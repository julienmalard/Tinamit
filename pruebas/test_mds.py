import unittest

from tinamit.EnvolturaMDS import generar_mds, EnvolturaMDS, ModeloVensim, ModeloPySD, ModeloVensimMdl
from tinamit.EnvolturaMDS.Vensim import dll_Vensim


class Test_ModeloSenc(unittest.TestCase):

    def setUp(símismo):
        print('setUp')
        símismo.modelos = {
            'mdlVensim': ModeloVensimMdl('recursos/prueba_senc.mdl'),
            'PySDVensim': ModeloPySD('recursos/prueba_senc.mdl')
        }  # type: dict[str, EnvolturaMDS]

        if dll_Vensim:
            símismo.modelos['dllVensim'] = ModeloVensim('recursos/prueba_senc.vpm')

        símismo.info_vars = {
            'Lluvia': {'unidades': 'm3', 'líms': (0, None)},
            'Nivel lago inicial': {'unidades': 'm3', 'líms': (0, None), 'val_inic': 1500},
            'Flujo río': {'unidades': 'm3/mes', 'líms': (0, None)},
            'Lago': {'unidades': 'm3', 'líms': (0, None)},
            'Evaporación': {'unidades': 'm3/mes', 'líms': (0, None)}
        }

        for mod in símismo.modelos.values():
            for v, d_v in símismo.info_vars.items():
                if 'val_inic' in d_v:
                    mod.inic_val(v, d_v['val_inic'])

            mod.simular(tiempo_final=200)

    def test_leer_vars(símismo):
        print('test_leer_vars')
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                vars_modelo = set(mod.variables)
                símismo.assertSetEqual(set(símismo.info_vars), vars_modelo)

    def prb_leer_info(símismo):

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertTrue(len(d_v['info']) > 0 for d_v in mod.variables.values())

    def prb_leer_unidades(símismo):

        unids = {v: d_v['unidades'] for v, d_v in símismo.info_vars.items()}

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                unids_mod = {v: d_v['unidades'] for v, d_v in mod.variables.items()}
                símismo.assertDictEqual(unids, unids_mod)

    def prb_leer_líms(símismo):
        unids = {v: d_v['líms'] for v, d_v in símismo.info_vars.items()}

        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                unids_mod = {v: d_v['líms'] for v, d_v in mod.variables.items()}
                símismo.assertDictEqual(unids, unids_mod)

    def prb_cmb_vals_inic(símismo):
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertEqual(mod.variables['Nivel lago inicial']['val'], 1500)

    def prb_simul(símismo):
        for mod in símismo.modelos.values():
            with símismo.subTest(mod=mod):
                símismo.assertAlmostEqual(mod.variables['Lago']['val'], 100)
