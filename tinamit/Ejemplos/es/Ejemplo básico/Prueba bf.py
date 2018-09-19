import random

from tinamit.BF import ModeloBF


class Envoltura(ModeloBF):

    def _incrementar(símismo, paso, guardar_cada=None):
        símismo.variables['Lluvia']['val'] = random.random() * símismo.variables['Bosques']['val'] / 1000000 * paso

    def _leer_vals(símismo):
        pass

    def _cambiar_vals_modelo_externo(símismo, valores):
        pass

    def _inic_dic_vars(símismo):
        símismo.variables['Lluvia'] = {'val': 1,
                                       'unidades': 'm*m*m/mes',
                                       'ingreso': False,
                                       'egreso': True,
                                       }
        símismo.variables['Bosques'] = {'val': 1000000,
                                        'unidades': 'm*m',
                                        'ingreso': True,
                                        'egreso': False,
                                        }

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        pass

    def unidad_tiempo(símismo):
        return "Meses"

    def cerrar_modelo(símismo):
        pass
