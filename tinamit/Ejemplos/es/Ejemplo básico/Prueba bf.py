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

    def iniciar_modelo(símismo, n_pasos, t_final, nombre_corrida, vals_inic):
        super().iniciar_modelo(n_pasos, nombre_corrida, vals_inic)

    def unidad_tiempo(símismo):
        return "Meses"

    def cerrar_modelo(símismo):
        pass
