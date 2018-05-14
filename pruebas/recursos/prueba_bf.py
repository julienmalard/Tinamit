import random

from tinamit.BF import ModeloBF


class ModeloPrueba(ModeloBF):

    def _cambiar_vals_modelo_interno(símismo, valores):
        pass

    def _incrementar(símismo, paso):
        símismo.variables['Lluvia']['val'] = random.random() * símismo.variables['Lago']['val'] / 10 * paso
        símismo.variables['Escala']['val'] += paso

    def _leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return 'años'

    def _inic_dic_vars(símismo):
        símismo.variables['Lluvia'] = {
            'val': 1,
            'unidades': 'm3/mes',
            'líms': (0, None),
            'ingreso': False,
            'egreso': True,
            'dims': (1,)
        }
        símismo.variables['Lago'] = {
            'val': 1000,
            'unidades': 'm3',
            'líms': (0, None),
            'ingreso': True,
            'egreso': False,
            'dims': (1,)
        }
        símismo.variables['Escala'] = {
            'val': 0,
            'unidades': '',
            'líms': (0, None),
            'ingreso': False,
            'egreso': True,
            'dims': (1,)
        }
        símismo.variables['Máx lluvia'] = {
            'val': 10,
            'unidades': 'm3/mes',
            'líms': (0, None),
            'ingreso': True,
            'egreso': False,
            'dims': (1,)
        }

    def leer_vals_inic(símismo):
        pass
