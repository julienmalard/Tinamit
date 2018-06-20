from random import random as alea

from tinamit.BF import ModeloBF


class ModeloPrueba(ModeloBF):

    def _cambiar_vals_modelo_interno(símismo, valores):
        pass

    def _incrementar(símismo, paso, guardar_cada=None):
        símismo._act_vals_dic_var({'Lluvia': símismo.obt_val_actual_var('Lago') / 10 * paso})
        símismo._act_vals_dic_var({'Escala': símismo.obt_val_actual_var('Escala') + 1})
        símismo._act_vals_dic_var({'Aleatorio': alea()})

    def _leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return 'años'

    def _inic_dic_vars(símismo):
        símismo.variables.clear()

        símismo.variables.update({
            'Lluvia': {
                'val': 1,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': (1,)
            },
            'Lago': {
                'val': 1000,
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': (1,)
            },
            'Escala': {
                'val': 0,
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
                'dims': (1,)
            },
            'Máx lluvia': {
                'val': 10,
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
                'dims': (1,)
            },
            'Aleatorio': {
                'val': 0,
                'unidades': 'Sdmn',
                'líms': (0, 1),
                'ingreso': False,
                'egreso': True,
                'dims': (1,)
            }
        }
        )

    def _leer_vals_inic(símismo):
        símismo.variables['Lluvia']['val'] = 1
        símismo.variables['Lago']['val'] = 1000
        símismo.variables['Escala']['val'] = 0
        símismo.variables['Máx lluvia']['val'] = 10
        símismo.variables['Aleatorio']['val'] = 0

    def paralelizable(símismo):
        return True
