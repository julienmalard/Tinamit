import os
import unittest

import pandas as pd

from tinamit.EnvolturasMDS import generar_mds

dir_act = os.path.split(__file__)[0]
arch_mds = os.path.join(dir_act, 'recursos/mod_enferm.mdl')


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

        cls.datos = pd.DataFrame(
            cls.mod.simular(
                tiempo_final=100,
                vars_interés=['Individuos Suceptibles', 'Individuos Infectados', 'Individuos Resistentes']
            )
        )

    def test_calibrar_con_optimización_rcem(símismo):
        símismo.mod.conectar_datos(símismo.datos)
        símismo.mod.conectar_var_a_datos(var='Individuos Suceptibles')
        símismo.mod.calibrar(
            paráms=list(símismo.paráms),
            líms_paráms={
                'taza de contacto': (0, 100),
                'taza de infección': (0.005, 0.009),
                'número inicial infectado': (0, 50),
                'taza de recuperación': (0.01, 0.05)
            },
            método='mc'
        )
