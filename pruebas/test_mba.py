import unittest

from tinamit.envolt.mba.mesa import ModeloMesa

from .recursos.mba.mba import ModeloDinero


class PruebaMBA(unittest.TestCase):
    def test_MBA(símismo):
        res = ModeloMesa(ModeloDinero, dict(N=10, width=15, height=15)).simular(100, 'mba')
        pass
