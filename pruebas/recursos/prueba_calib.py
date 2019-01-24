from __future__ import division

from tinamit.Modelo import Modelo
import numpy as np


class ModeloCalibEstático(Modelo):

    def __init__(símismo, nombre='prueba'):
        super().__init__(nombre=nombre)

        símismo.valores = None  # type: np.ndarray
        símismo.i = 0

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        # function
        símismo._calcular_func(tiempo_final, vals_inic)
        símismo.i = 0

    def _cambiar_vals_modelo_externo(símismo, valores):
        pass

    def _incrementar(símismo, paso, guardar_cada=None):
        símismo.i += paso
        símismo.cambiar_vals({'y': símismo.valores[símismo.i]})

    def _leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return 'años'

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def _leer_vals_inic(símismo):
        símismo.cambiar_vals({'y': símismo.valores[0]})

    def paralelizable(símismo):
        return True

    def _calcular_func(símismo, tiempo_final, vals_inic):
        raise NotImplementedError


class ModeloLogisticCalib(ModeloCalibEstático):
    def _inic_dic_vars(símismo):
        símismo.variables.clear()

        # símismo.variables.update({
        #     'A': {
        #         'val': np.zeros(5),  # np.zeros(6)
        #         'unidades': 'm3/mes',
        #         'líms': (0, None),
        #         'ingreso': False,
        #         'egreso': True,
        #         'dims': (5,)  # 6
        #     },
        #     'B': {
        #         'val': np.zeros(5),
        #         'unidades': 'm3',
        #         'líms': (0, None),
        #         'ingreso': True,
        #         'egreso': False,
        #         'dims': (5,)
        #     },
        #     'y': {'val': np.zeros(5),
        #           'unidades': 'm3',
        #           'líms': (0, None),
        #           'ingreso': True,
        #           'egreso': False,
        #           'dims': (5,)}
        #
        # }
        # )

        símismo.variables.update({
            'A': {
                'val': np.zeros(6, ),  # 1,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': (6,)
            },
            'B': {
                'val': np.zeros(6, ),  # 0.3,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': (6,)
            },
            'C': {
                'val': np.zeros(6, ),  # 1,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': (6,)
            },
            'y': {'val': np.zeros(6, ),
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': (6,)}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        c = vals_inic['C']
        x = np.arange(tiempo_final + 1)[..., np.newaxis]
        símismo.valores = a / (1 + np.exp(-b * x + c))
