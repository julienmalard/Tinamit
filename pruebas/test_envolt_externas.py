import unittest

from tinamit.envolt.bf.sahysmod import ModeloSAHYSMOD
from tinamit.envolt.mds import ModeloPySD, ModeloVensimDLL
from tinamit.mod.prbs import verificar_leer_ingr, verificar_leer_egr

_envolts = [ModeloSAHYSMOD, ModeloPySD, ModeloVensimDLL]


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
                arch_ingr = cls.prb_ingreso()
                arch_egr = cls.prb_egreso()
                if arch_ingr and arch_egr and cls.instalado():
                    mod = cls(arch_ingr)
                    mod.simular(2)
