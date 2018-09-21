from random import random as alea

from tinamit.BF import ModeloBF


class ModeloPrueba(ModeloBF):

    def __init__(símismo, unid_tiempo='años', nombre='modeloBF'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre)

    def _cambiar_vals_modelo_externo(símismo, valores):
        pass

    def _incrementar(símismo, paso, guardar_cada=None):
        símismo._act_vals_dic_var({'Lluvia': símismo.obt_val_actual_var('Lago') / 10 * paso})
        símismo._act_vals_dic_var({'Escala': símismo.obt_val_actual_var('Escala') + paso})
        símismo._act_vals_dic_var({'Aleatorio': alea()})

    def _leer_vals(símismo):
        pass

    def cerrar_modelo(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def _inic_dic_vars(símismo):
        símismo.variables.clear()

        símismo.variables.update({
            'Lluvia': {
                'unidades': 'm3/mes',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
            },
            'Lago': {
                'unidades': 'm3',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
            },
            'Escala': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': False,
                'egreso': True,
            },
            'Vacío': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
            },
            'Vacío2': {
                'unidades': '',
                'líms': (0, None),
                'ingreso': True,
                'egreso': False,
            },
            'Aleatorio': {
                'unidades': 'Sdmn',
                'líms': (0, 1),
                'ingreso': False,
                'egreso': True,
            }
        })

    def _vals_inic(símismo):
        return {'Lluvia': 1, 'Lago': 1000, 'Escala': 0, 'Vacío': 10, 'Vacío2': 10, 'Aleatorio': 0}

    def paralelizable(símismo):
        return True
