from tinamit.Análisis.Números import tx_a_núm

import unittest


class Test_TradsUnids(unittest.TestCase):

    def test_traducir_entero(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५'), 12345)

    def test_traducir_decimal(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५.६७८९'), 12345.6789)

    def test_traducir_negativo(símismo):
        símismo.assertEqual(tx_a_núm('-१२३४५.६७८९'), -12345.6789)

    def test_traducir_notación_científica(símismo):
        símismo.assertAlmostEqual(tx_a_núm('-१२३४५.६७८९e-१'), -1234.56789)