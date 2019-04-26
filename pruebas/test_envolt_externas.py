import unittest

from tinamit.envolt.bf.sahysmod import ModeloSAHYSMOD
from tinamit.mod.prbs import verificar_leer_ingr, verificar_leer_egr, verificar_simul

_envolts = [ModeloSAHYSMOD]


class TestEnvolturasExtern(unittest.TestCase):

    def test_leer_ingreso(símismo):
        for cls in _envolts:
            with símismo.subTest(envlt=cls.__name__):
                verificar_leer_ingr(símismo, cls)

    def test_leer_egreso(símismo):
        for cls in _envolts:
            with símismo.subTest(envlt=cls.__name__):
                verificar_leer_egr(símismo, cls)

    def test_correr_modelo(símismo):
        for cls in _envolts:
            with símismo.subTest(envlt=cls.__name__):
                verificar_simul(símismo, cls)
