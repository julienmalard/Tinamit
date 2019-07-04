import unittest

from tinamit.config import conf, trads


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conf['prueba'] = 1

    def test_obt_val_config(símismo):
        símismo.assertEqual(conf['prueba'], 1)

    def test_obt_val_config_anidada(símismo):
        conf['prueba2', 'prueba3'] = '¡aquí estoy!'
        símismo.assertEqual('¡aquí estoy!', conf['prueba2', 'prueba3'])

    def test_borrrar_config_no_existe(símismo):
        with símismo.assertRaises(KeyError):
            conf.borrar('Yo no existo')

    @classmethod
    def tearDownClass(cls):
        conf.borrar('prueba')
        conf.borrar('prueba2')


class TestCambiarLengua(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.leng = trads.idioma()
        cls.lengs_aux = trads.auxiliares()

    def test_cambiar_leng(símismo):
        trads.cambiar_idioma('tzj')
        símismo.assertEqual(trads.idioma(), 'tzj')

    def test_cambiar_lengs_aux(símismo):
        trads.cambiar_aux('हिं')
        símismo.assertListEqual(trads.auxiliares(), ['हिं'])

    @classmethod
    def tearDownClass(cls):
        trads.cambiar_idioma(cls.leng)
        trads.cambiar_aux(cls.lengs_aux)
