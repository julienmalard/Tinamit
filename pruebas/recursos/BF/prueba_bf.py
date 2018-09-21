from random import random as alea

from tinamit.BF import ModeloBF

d_vars = {
    'Lluvia': {
        'val': 1,
        'unidades': 'm3/mes',
        'líms': (0, None),
        'ingreso': False,
        'egreso': True,
    },
    'Lago': {
        'val': 1000,
        'unidades': 'm3',
        'líms': (0, None),
        'ingreso': True,
        'egreso': False,
    },
    'Escala': {
        'val': 0,
        'unidades': '',
        'líms': (0, None),
        'ingreso': False,
        'egreso': True,
    },
    'Vacío': {
        'val': 10,
        'unidades': 'm3/mes',
        'líms': (0, None),
        'ingreso': True,
        'egreso': False,
    },
    'Aleatorio': {
        'val': 0,
        'unidades': 'Sdmn',
        'líms': (0, 1),
        'ingreso': False,
        'egreso': True,
    }
}


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

        símismo.variables.update(d_vars)

    def _leer_vals_inic(símismo):
        símismo.variables['Lluvia']['val'] = 1
        símismo.variables['Lago']['val'] = 1000
        símismo.variables['Escala']['val'] = 0
        símismo.variables['Vacío']['val'] = 10
        símismo.variables['Aleatorio']['val'] = 0

    def paralelizable(símismo):
        return True

    def _reinic_vals(símismo):
        símismo.cambiar_vals({vr: d_vr['val'] for vr, d_vr in d_vars.items()})
