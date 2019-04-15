from random import random as alea

from tinamit import Modelo
from tinamit.mod import VariablesMod, Variable


class ModeloPrueba(Modelo):

    def __init__(símismo, unid_tiempo='años', nombre='modeloBF'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    def incrementar(símismo, corrida):
        símismo._act_vals_dic_var({'Lluvia': símismo.obt_val_actual_var('Lago') / 10 * paso})
        símismo._act_vals_dic_var({'Escala': símismo.obt_val_actual_var('Escala') + paso})
        símismo._act_vals_dic_var({'Aleatorio': alea()})

    @staticmethod
    def _gen_vars():
        return VariablesMod([
            Variable('Escala', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('Vacío', unid=None, ingr=True, egr=False, líms=(0, None)),
            Variable('Vacío2', unid=None, ingr=True, egr=False, líms=(0, None)),
            Variable('Aleatorio', unid=None, ingr=False, egr=True, líms=(0, 1))
        ])

    def _leer_vals(símismo):
        pass

    def cerrar(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def _vals_inic(símismo):
        return {'Lluvia': 1, 'Lago': 1000, 'Escala': 0, 'Vacío': 10, 'Vacío2': 10, 'Vacío3': 10, 'Aleatorio': 0}

    def paralelizable(símismo):
        return True
