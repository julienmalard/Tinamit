from random import random as alea

from tinamit.mod import VariablesMod, Variable, Modelo


class ModeloPrueba(Modelo):

    def __init__(símismo, unid_tiempo='años', nombre='modeloBF'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    def incrementar(símismo, corrida):
        pasos = corrida.eje_tiempo.pasos_avanzados(símismo.unidad_tiempo())
        símismo.variables.cambiar_vals(
            {'Escala': símismo.variables['Escala'].obt_val() + pasos,
             'Aleatorio': alea()})

    @staticmethod
    def _gen_vars():
        return VariablesMod([
            Variable('Escala', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('Vacío', unid=None, ingr=True, egr=False, líms=(0, None)),
            Variable('Vacío2', unid=None, ingr=True, egr=False, líms=(0, None)),
            Variable('Aleatorio', unid=None, ingr=False, egr=True, líms=(0, 1))
        ])

    def cerrar(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def _vals_inic(símismo):
        return {'Lluvia': 1, 'Lago': 1000, 'Escala': 0, 'Vacío': 10, 'Vacío2': 10, 'Vacío3': 10, 'Aleatorio': 0}

    def paralelizable(símismo):
        return True
