import random

from tinamit.NuevoBF import ClaseModeloBF


class Modelo(ClaseModeloBF):

    def ejec(símismo):
        pass

    def incrementar(símismo, paso):

        símismo.variables['var1']['var'] = random.random() * 10 * símismo.variables['var2']['var'] * paso

    def leer_vals(símismo):
        pass

    def cambiar_vals(símismo, valores):
        pass

    def inic_vars(símismo):
        símismo.variables['var1'] = {'va1': 5,
                                     'unidades': 'kg/ha',
                                     'ingreso': False,
                                     'egreso': True,
                                     }
        símismo.variables['var2'] = {'va1': 2,
                                     'unidades': 'cm/día',
                                     'ingreso': True,
                                     'egreso': False,
                                     }

    def iniciar_modelo(símismo, **kwargs):
        pass

    def obt_unidad_tiempo(símismo):
        return "Meses"

    def cerrar_modelo(símismo):
        pass
