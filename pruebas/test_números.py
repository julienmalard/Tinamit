from tinamit.Análisis.Números import tx_a_núm

import unittest


class Test_TradsUnids(unittest.TestCase):

    def test_traducir_entero(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५'), 12345)

    def test_traducir_decimal(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५.६७८९'), 12345.6789)

    def test_traducir_decimal_coma(símismo):
        símismo.assertEqual(tx_a_núm('१२३४५,६७८९'), 12345.6789)

    def test_traducir_negativo(símismo):
        símismo.assertEqual(tx_a_núm('-१२३४५.६७८९'), -12345.6789)

    def test_traducir_notación_científica(símismo):
        símismo.assertAlmostEqual(tx_a_núm('-१२३४५.६७८९e-१'), -1234.56789)

    def test_traducir_sistema_bases(símismo):
        símismo.assertEqual(tx_a_núm('௰௨௲௩௱௪௰௫'), 12345)

    def test_traducir_sistema_bases_con_decimal(símismo):
        símismo.assertEqual(tx_a_núm('௰௨௲௩௱௪௰௫.௬௭௮௯'), 12345.6789)

    def test_traducir_sistema_bases_notación_científica(símismo):
        símismo.assertEqual(tx_a_núm('௰௨௲௩௱௪௰௫.௬௭௮௯e௧'), 123456.789)

    def test_traducir_sistema_bases_chino(símismo):
        símismo.assertEqual(tx_a_núm('三百二十一'), 321)

    def test_traducir_número_erróneo(símismo):
        with símismo.assertRaises(ValueError):
            tx_a_núm('abcd')
