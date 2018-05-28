import os
import unittest


from tinamit.Análisis.Datos import DatosIndividuales, DatosRegión, SuperBD


dir_act = os.path.split(__file__)[0]
arch_reg = os.path.join(dir_act, 'recursos/datos/datos_reg.csv')
arch_indiv = os.path.join(dir_act, 'recursos/datos/datos_indiv.csv')


class Test_SuperBD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bd_región = DatosRegión(nombre='prueba regional', archivo=arch_reg, fecha='fecha', lugar='lugar')
        bd_indiv = DatosIndividuales(nombre='prueba individual', archivo=arch_indiv, fecha='fecha', lugar='lugar')
        cls.bd = SuperBD(nombre='BD Central', bds=[bd_región, bd_indiv])

