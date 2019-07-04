import os
import unittest

import numpy as np
from numpy import testing as npt

from pruebas.recursos.bf.prueba_bf import PruebaBF
from pruebas.recursos.bf.variantes import EjDeterminado, EjBloques, EjIndeterminado
from tinamit.envolt.bf import gen_bf, ModeloBF

dir_act = os.path.split(__file__)[0]
arch_bf = os.path.join(dir_act, 'recursos/bf/prueba_mod.py')


class TestModeloDeter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = EjDeterminado(tmñ_ciclo=5).simular(50)

    def test_paso(símismo):
        npt.assert_equal(símismo.res['paso'].vals.values.flatten(), np.arange(51))

    def test_ciclo(símismo):
        npt.assert_equal(símismo.res['ciclo'].vals.values.flatten(), np.concatenate(([0], np.repeat(np.arange(1, 11), 5))))

    def test_i_en_ciclo(símismo):
        npt.assert_equal(símismo.res['i_en_ciclo'].vals.values.flatten(), np.concatenate(([4], np.tile(np.arange(5), 10))))


class TestModeloIndeter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = EjIndeterminado(rango_n=(3, 7)).simular(50)

    def test_paso(símismo):
        npt.assert_equal(símismo.res['paso'].vals.values.flatten(), np.arange(51))

    def test_ciclo(símismo):
        ciclo = símismo.res['ciclo'].vals.values.flatten()
        npt.assert_equal(np.unique(ciclo), np.arange(len(np.unique(ciclo))))
        símismo.assertTrue(all(np.sum(ciclo == c) <= 7 for c in np.unique(ciclo)))


class TestModeloBloques(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = EjBloques(tmñ_bloques=[3, 4, 5]).simular(36)

    def test_paso(símismo):
        npt.assert_equal(símismo.res['paso'].vals.values.flatten(), np.arange(37))

    def test_ciclo(símismo):
        npt.assert_equal(
            símismo.res['ciclo'].vals.values.flatten(), np.concatenate(([0], np.repeat(np.arange(1, 4), 12)))
        )

    def test_bloque(símismo):
        npt.assert_equal(
            símismo.res['bloque'].vals.values.flatten(),
            np.concatenate(([2], np.tile(np.repeat([0, 1, 2], [3, 4, 5]), 3)))
        )

    def test_i_en_ciclo(símismo):
        npt.assert_equal(
            símismo.res['i_en_ciclo'].vals.values.flatten(), np.concatenate(([11], np.tile(np.arange(12), 3)))
        )


class TestGenAuto(unittest.TestCase):
    def test_instancia(símismo):
        mod = gen_bf(PruebaBF())
        símismo.assertIsInstance(mod, ModeloBF)

    def test_clase(símismo):
        mod = gen_bf(PruebaBF)
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_instancia(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_instancia.py'))
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_clase(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_clase.py'))
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_instancia_no_identificada(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_instancia_no_identificada.py'))
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_clase_no_identificada(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_clase_no_identificada.py'))
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_múltiples(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_múltiples.py'))
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_múltiples_no_identificada(símismo):
        mod = gen_bf(símismo._obt_recurso('arch_múltiples_no_identificada.py'))
        símismo.assertIsInstance(mod, ModeloBF)

    def test_archivo_vacío(símismo):
        with símismo.assertRaises(AttributeError):
            gen_bf(símismo._obt_recurso('arch_vacío.py'))

    def test_tipo_no_válido(símismo):
        with símismo.assertRaises(TypeError):
            gen_bf(123)

    def test_archivo_no_existe(símismo):
        with símismo.assertRaises(FileNotFoundError):
            gen_bf('નમસ્તે')

    def test_archivo_no_python(símismo):
        with símismo.assertRaises(ValueError):
            gen_bf(símismo._obt_recurso('no_python.txt'))

    @staticmethod
    def _obt_recurso(archivo):
        return os.path.join('recursos/bf/_prbs_arch', archivo)
