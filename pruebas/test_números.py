from warnings import warn

from tinamit.Análisis.Números import tx_a_núm

import unittest


class Test_TradsUnids(unittest.TestCase):
    warn('Test_TradsUnids')

    def test_traducir_entero(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५'), 12345)

    def test_traducir_decimal(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५.६७८९'), 12345.6789)

    def test_traducir_negativo(símismo):
        símismo.assertEqual(tx_a_núm('-१२३४५.६७८९'), -12345.6789)

    def test_traducir_notación_científica(símismo):
        símismo.assertAlmostEqual(tx_a_núm('-१२३४५.६७८९e-१'), -1234.56789)

    def test_traducir_sistema_bases(símismo):
        símismo.assertEqual(tx_a_núm('௰௨௲௩௱௪௰௫.௬௭௮௯'), 12345.6789)