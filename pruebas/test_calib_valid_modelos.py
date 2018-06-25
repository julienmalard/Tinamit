import os
import unittest

from tinamit.Geog import Geografía
from tinamit.EnvolturasMDS import generar_mds

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/mod_enferm.mdl')
arch_csv_geog = os.path.join(dir_act, 'recursos/datos/prueba_geog.csv')


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
        for var, val in cls.paráms.items():
            cls.mod.inic_val_var(var, val)

        cls.datos = cls.mod.simular(
                tiempo_final=100,
                vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
            )

    def test_calibrar_validar(símismo):
        símismo.mod.conectar_datos(símismo.datos)
        símismo.mod.calibrar(
            paráms=list(símismo.paráms),
            líms_paráms={
                'taza de contacto': (0, 100),
                'taza de infección': (0, 0.02),
                'número inicial infectado': (0, 50),
                'taza de recuperación': (0, 0.1)
            }
        )
        símismo.assertTrue(símismo.mod.validar()['éxito'])

    @classmethod
    def tearDownClass(cls):
        # Limpiamos todos los documentos temporarios generados por los algoritmos de calibración.
        for c in os.walk('.'):
            for a in c[2]:
                nmbr, ext = os.path.splitext(a)
                if nmbr.startswith('CalibTinamït') and ext == '.csv':
                    try:
                        os.remove(a)
                    except (PermissionError, FileNotFoundError):
                        pass


class Test_CalibModloEspacial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paráms = {
            'taza de contacto': {'708': 81.25, '1010': 50},
            'taza de infección': {'708': 0.007, '1010': 0.005},
            'número inicial infectado': {'708': 22.5, '1010': 40},
            'taza de recuperación': {'708': 0.0375, '1010': 0.050}
        }
        cls.mod = generar_mds(arch_mds)
        cls.mod.geog = Geografía('prueba', archivo=arch_csv_geog)
        cls.datos = cls.mod.simular(tiempo_final=200, escala='muni')

        cls.mod.conectar_datos(cls.datos)

    def test_calib_valid_espacial(símismo):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
