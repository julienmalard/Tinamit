import os
import unittest

from pruebas.recursos.BF.prueba_forma import ModeloLogistic
from pruebas.test_mds import limpiar_mds
from tinamit.EnvolturasMDS import generar_mds
from tinamit.Geog import Geografía

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/MDS/mod_enferm.mdl')
arch_csv_geog = os.path.join(dir_act, 'recursos/datos/prueba_geog.csv')

líms_paráms = {
    'taza de contacto': (0, 100),
    'taza de infección': (0, 0.02),
    'número inicial infectado': (0, 50),
    'taza de recuperación': (0, 0.1)
}


class Test_CalibModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paráms = {
            'taza de contacto': 81.25,
            'taza de infección': 0.007,
            'número inicial infectado': 22.5,
            'taza de recuperación': 0.0375
        }
        cls.mod = generar_mds(arch_mds)

        cls.datos = cls.mod.simular(
            t_final=20,
            vals_inic=cls.paráms,
            vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
        )

    def test_calibrar_validar(símismo):
        símismo.mod.calibrar(
            paráms=list(símismo.paráms),
            líms_paráms=líms_paráms,
            bd=símismo.datos
        )
        símismo.assertTrue(símismo.mod.validar(bd=símismo.datos)['éxito'])


class Test_CalibModeloEspacial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paráms = {
            'taza de contacto': {'708': 81.25, '1010': 50},
            'taza de infección': {'708': 0.007, '1010': 0.005},
            'número inicial infectado': {'708': 22.5, '1010': 40},
            'taza de recuperación': {'708': 0.0375, '1010': 0.050}
        }
        cls.mod = mod = generar_mds(arch_mds)
        mod.geog = Geografía('prueba', archivo=arch_csv_geog)
        mod.cargar_calibs(cls.paráms)
        cls.datos = mod.simular_en(
            t_final=20, en=['708', '1010'],
            vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
        )
        mod.borrar_calibs()

    def test_calib_valid_espacial(símismo):
        símismo.mod.calibrar(paráms=list(símismo.paráms), bd=símismo.datos, líms_paráms=líms_paráms)
        valid = símismo.mod.validar(
            bd=símismo.datos,
            var=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
        )
        símismo.assertTrue(valid['éxito'])

    @classmethod
    def tearDownClass(cls):
        limpiar_mds()

class Test_CalibModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paráms = {
            'A': 5,
            'B': 2,
            'C': 4,
        }
        cls.mod = ModeloLogistic()

        cls.datos = cls.mod.simular(
            t_final=20,
            vals_inic=cls.paráms,
            vars_interés=['A', 'B', 'C']
        )

    def test_calibrar_validar(símismo):
        símismo.mod.calibrar(
            paráms=list(símismo.paráms),
            líms_paráms= {'A': (3, 10), 'B': (0.5, 2), 'C': (3, 5)},
            bd=símismo.datos
        )
        símismo.assertTrue(símismo.mod.validar(bd=símismo.datos)['éxito'])

