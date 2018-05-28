import unittest


from tinamit.Análisis.Datos import DatosIndividuales, DatosRegión, SuperBD


class Test_SuperBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bd_región = DatosRegión()
        bd_indiv = DatosIndividuales()
        cls.bd = SuperBD()

