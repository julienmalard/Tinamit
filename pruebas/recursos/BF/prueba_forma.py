"""
Python model "mod_prueba_sens.py"
For Sensitivity Analysis
"""
from __future__ import division

from tinamit.Modelo import Modelo
import numpy as np


class ModeloEstático(Modelo):

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        pass

    def _cambiar_vals_modelo_externo(símismo, valores):
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


class PlantillaForma(Modelo):

    def __init__(símismo, nombre='prueba', dims=(1,)):

        símismo.dims = dims

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
        símismo.cambiar_vals({'y': símismo.valores[símismo.i, ...]})

    @staticmethod
    def _gen_x_tiempo(tiempo_final, l_vars):
        x = np.arange(tiempo_final + 1)

        assert all(isinstance(v, np.ndarray) for v in l_vars) or all(not isinstance(v, np.ndarray) for v in l_vars)

        v = l_vars[0]
        if isinstance(v, np.ndarray):
            tmñ = v.shape
            if not all(v_2.shape == tmñ for v_2 in l_vars[1:]):
                raise ValueError

            x = x.reshape((tiempo_final + 1, *[1] * len(tmñ)))

        return x

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


class ModeloLinear(PlantillaForma):

    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.ones(dims) if multidim else 1,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.zeros(dims) if multidim else 0,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.ones(dims) if multidim else 1,
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b])
        símismo.valores = a * x + b + np.random.normal(scale=0.1, size=x.shape)


class ModeloExpo(PlantillaForma):

    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.full(dims, 0.1) if multidim else 0.1,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.full(dims, 1.1) if multidim else 1.1,
                'unidades': 'm3',
                'líms': (0, 2),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.full(dims, 0.2) if multidim else 0.2,
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b])
        símismo.valores = a * (b ** x) + np.random.normal(scale=0.1, size=x.shape)


class ModeloLogistic(PlantillaForma):
    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.full(dims, 5) if multidim else 5,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.full(dims, 0.85) if multidim else 0.85,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'C': {
                'val': np.full(dims, 3) if multidim else 3,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.full(dims, 1) if multidim else 1,
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        c = vals_inic['C']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b, c])
        símismo.valores = a / (1 + np.exp(-b * x + c)) + np.random.normal(scale=0.01)


class ModeloInverso(PlantillaForma):
    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.full(dims, 3) if multidim else 3,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.full(dims, 0.4) if multidim else 0.4,
                'unidades': 'm3',
                'líms': (0.4, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.full(dims, 2.1) if multidim else 2.1,
                  'unidades': 'm3',
                  'líms': (None, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b])
        símismo.valores = a / (x + b) + np.random.normal(scale=0.1, size=x.size)


class ModeloLog(PlantillaForma):
    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.full(dims, 0.3) if multidim else 0.3,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.full(dims, 0.1) if multidim else 0.1,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.full(dims, 1) if multidim else 1,
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b])
        símismo.valores = a * np.log(x + b) + np.random.normal(scale=0.1, size=x.size)


class ModeloOscil(PlantillaForma):
    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.full(dims, 0.7) if multidim else 0.7,
                'unidades': 'm3/mes',
                'líms': (0.1, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.full(dims, 0.6) if multidim else 0.6,
                'unidades': 'm3',
                'líms': (1, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'C': {
                'val': np.full(dims, 1) if multidim else 1,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.full(dims, 0.55) if multidim else 0.55,
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        c = vals_inic['C']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b, c])
        símismo.valores = a * np.sin(b * x + c) + np.random.normal(scale=0.1, size=x.size)


class ModeloOscilAten(PlantillaForma):
    def _inic_dic_vars(símismo):
        dims = símismo.dims
        multidim = dims != (1,)

        símismo.variables.clear()

        símismo.variables.update({
            'A': {
                'val': np.full(dims, 0.1) if multidim else 0.1,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': dims
            },
            'B': {
                'val': np.full(dims, 0.7) if multidim else 0.7,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'C': {
                'val': np.full(dims, 0.6) if multidim else 0.6,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'D': {
                'val': np.full(dims, 1.1) if multidim else 1.1,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': dims
            },
            'y': {'val': np.full(dims, 1) if multidim else 1,
                  'unidades': 'm3',
                  'líms': (0, None),
                  'ingreso': True,
                  'egreso': False,
                  'dims': dims}

        }
        )

    def _calcular_func(símismo, tiempo_final, vals_inic):
        a = vals_inic['A']
        b = vals_inic['B']
        c = vals_inic['C']
        d = vals_inic['D']
        x = símismo._gen_x_tiempo(tiempo_final, l_vars=[a, b, c, d])
        símismo.valores = np.exp(a * x) * b * np.sin(c * x + d) + np.random.normal(scale=0.1, size=x.size)
