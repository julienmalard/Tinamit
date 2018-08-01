"""
Python model "mod_prueba_sens.py"
For Sensitivity Analysis
"""
from __future__ import division

from tinamit.BF import ModeloBF
import numpy as np


class ModeloPrueba(ModeloBF):

    def _cambiar_vals_modelo_interno(símismo, valores):
        pass

    def _incrementar(símismo, paso, guardar_cada=None):
        pass

    def _leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return 'años'

    def _inic_dic_vars(símismo):
        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.zeros(6),
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': (6,)
            },
            'B': {
                'val': np.zeros(6),
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': (6,)
            },
            'C': {
                'val': np.zeros(6),
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': (6,)
            },
            'D': {
                'val': np.zeros(6),
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': (6,)
            },
            'E': {
                'val': np.zeros(6),
                'unidades': 'Sdmn',
                'líms': (0, 1),
                'ingreso': False,
                'egreso': True,
                'dims': (6,)
            }
        }
        )

    def _leer_vals_inic(símismo):
        pass

    def paralelizable(símismo):
        return True

