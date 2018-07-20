import unittest

from tinamit.config import obt_val_config, poner_val_config, borrar_var_config, cambiar_lengua


class Test_Config(unittest.TestCase):
    def test_obt_val_config(símismo):
        val = obt_val_config('leng')
        símismo.assertIsInstance(val, str)

    def test_obt_val_config_con_condición(símismo):
        def cond(x):
            return True

        símismo.assertIsInstance(obt_val_config('leng', cond=cond), str)

    def test_obt_val_config_con_condición_falsa(símismo):
        def cond(x):
            return False

        símismo.assertIs(obt_val_config('leng', cond=cond, mnsj_err=''), None)

    def test_obt_val_config_con_auto(símismo):
        símismo.assertEqual(obt_val_config('jaja', autos='abc'), 'abc')

    def test_obt_val_config_con_auto_y_cond(símismo):
        def cond(x):
            return x[0] == 'a'

        símismo.assertEqual(obt_val_config('leng', cond=cond, autos=['cba', 'abc']), 'abc')

    def test_poner_val_config(símismo):
        poner_val_config('prueba', 'JAJA')
        símismo.assertEqual('JAJA', obt_val_config('prueba'))

    def test_obt_val_config_anidada(símismo):
        poner_val_config(['prueba', 'prueba2'], '¡aquí estoy!')
        símismo.assertEqual('¡aquí estoy!', obt_val_config(['prueba', 'prueba2']))

    def test_borrrar_config_no_existe(símismo):
        with símismo.assertRaises(KeyError):
            borrar_var_config('Yo no existo')

    @classmethod
    def tearDownClass(cls):
        try:
            borrar_var_config('prueba')
        except KeyError:
            pass


class Test_CambiarLengua(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.leng = obt_val_config('leng')
        cls.lengs_aux = obt_val_config('lengs_aux')

    def test_cambiar_leng(símismo):
        cambiar_lengua('tzj')
        símismo.assertEqual(obt_val_config('leng'), 'tzj')

    def test_cambiar_lengs_aux(símismo):
        cambiar_lengua('த', auxiliares='हिं')
        símismo.assertEqual(obt_val_config('leng'), 'த')
        símismo.assertListEqual(obt_val_config('lengs_aux'), ['हिं'])

    @classmethod
    def tearDownClass(cls):
        cambiar_lengua(cls.leng, auxiliares=cls.lengs_aux)
