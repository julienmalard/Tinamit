import os
import unittest


from tinamit.Geog.Geog import Geografía

dir_act = os.path.split(__file__)[0]
arch_csv_geog = os.path.join(dir_act, 'recursos/prueba_geog.csv')


class Test_Geografía(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.geog = Geografía(nombre='Prueba Guatemala')
        cls.geog.agregar_info_regiones(archivo=arch_csv_geog)

    def test_nombre_a_cód_no_ambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Panajachel')
        símismo.assertEqual(cód, '710')

    def test_nombre_a_cód_ambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Sololá')
        símismo.assertIn(cód, ['7', '701'])

    def test_nombre_a_cód_desambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Sololá', escala='departamento')
        símismo.assertEqual(cód, '7')

    def test_obt_lugares_en_región(símismo):
        lgs = símismo.geog.obt_lugares_en('7')
        símismo.assertEqual(len(lgs), 19)
        símismo.assertTrue(all(símismo.geog.en_región(lg, '7') for lg in lgs))

    def test_obt_lugares_en_con_escala(símismo):
        lgs = símismo.geog.obt_lugares_en(escala='departamento')
        símismo.assertListEqual(lgs, [str(x) for x in range(1, 23)])
