import os
import unittest

import numpy as np

from tinamit.Geog.Geog import Geografía

dir_act = os.path.split(__file__)[0]
arch_csv_geog = os.path.join(dir_act, 'recursos/prueba_geog.csv')
arch_frm_regiones = os.path.join(dir_act, 'recursos/frm/munis.shp')
arch_frm_otra = os.path.join(dir_act, 'recursos/frm/otra_frm.shp')


class Test_Geografía(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.geog = Geografía(nombre='Prueba Guatemala')
        cls.geog.espec_estruct_geog(archivo=arch_csv_geog)

    def test_nombre_a_cód_no_ambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Panajachel')
        símismo.assertEqual(cód, '710')

    def test_nombre_a_cód_ambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Sololá')
        símismo.assertIn(cód, ['7', '701'])

    def test_nombre_a_cód_desambig(símismo):
        cód = símismo.geog.nombre_a_cód(nombre='Sololá', escala='departamento')
        símismo.assertEqual(cód, '7')

    def test_nombre_a_cód_erróneo(símismo):
        with símismo.assertRaises(ValueError):
            símismo.geog.nombre_a_cód(nombre='¡Yo no existo!')

    def test_obt_lugares_en_región(símismo):
        lgs = símismo.geog.obt_lugares_en('7')
        símismo.assertEqual(len(lgs), 19)
        símismo.assertTrue(all(símismo.geog.en_región(lg, '7') for lg in lgs))

    def test_obt_lugares_en_región_cód_numérico(símismo):
        ref = símismo.geog.obt_lugares_en('1')
        lgs = símismo.geog.obt_lugares_en(1)
        símismo.assertListEqual(ref, lgs)

    def test_obt_lugares_en_con_escala(símismo):
        lgs = símismo.geog.obt_lugares_en(escala='departamento')
        símismo.assertListEqual(lgs, [str(x) for x in range(1, 23)])

    def test_obt_lugares_en_con_escala_errónea(símismo):
        with símismo.assertRaises(ValueError):
            símismo.geog.obt_lugares_en(escala='¡Yo soy una escala que no existe!')

    def test_obt_todos_lugares(símismo):
        lgs = símismo.geog.obt_todos_lugares_en()
        símismo.assertTrue(all(x in lgs for x in ['7', '701', '708', 'T1']))

    def test_obt_todos_lugares_en_región(símismo):
        lgs = símismo.geog.obt_todos_lugares_en(en='7')
        símismo.assertSetEqual(set(lgs), set(str(x) for x in range(701, 720)))

    def test_obt_jerarquía(símismo):
        jrq = símismo.geog.obt_jerarquía(escala='municipio')
        munis = símismo.geog.obt_lugares_en(escala='municipio')
        trtrs = símismo.geog.obt_lugares_en(escala='territorio')
        deptos = símismo.geog.obt_lugares_en(escala='departamento')

        símismo.assertTrue(set(munis + trtrs).issubset(set(jrq)) or set(munis + deptos).issubset(set(jrq)))
        símismo.assertTrue(all([jrq[x] is None for x in jrq if x not in munis]))

    def test_obt_jerarquía_con_orden(símismo):
        jrq = símismo.geog.obt_jerarquía(escala='municipio', orden_jerárquico=['departamento'])
        munis = símismo.geog.obt_lugares_en(escala='municipio')
        deptos = símismo.geog.obt_lugares_en(escala='departamento')

        símismo.assertTrue(set(munis + deptos).issubset(set(jrq)))
        símismo.assertTrue(all([jrq[d] is None for d in deptos]))

    def test_agregar_y_quitar_forma(símismo):
        símismo.geog.agregar_forma(arch_frm_otra, nombre='bosque')
        símismo.assertIn('bosque', símismo.geog.formas)
        símismo.geog.quitar_forma('bosque')
        símismo.assertNotIn('bosque', símismo.geog.formas)

    def test_agregar_y_quitar_forma_regiones(símismo):
        símismo.geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI')
        símismo.assertIn('municipio', símismo.geog.formas_reg)
        símismo.geog.quitar_forma('municipio')
        símismo.assertNotIn('municipio', símismo.geog.formas_reg)

    def test_dibujar_desde_matriz_numpy(símismo):
        símismo.geog.agregar_frm_regiones(arch_frm_regiones, col_id='COD_MUNI')
        lugares = símismo.geog.obt_lugares_en(escala='municipio')
        símismo.geog.dibujar(archivo='prueba.jpg', valores=np.random.rand(len(lugares)), ids=lugares)
        símismo.assertTrue(os.path.isfile('prueba.jpg'))
        os.remove('prueba.jpg')
