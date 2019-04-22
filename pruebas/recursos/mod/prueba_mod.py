import random

from tinamit.mod import VariablesMod, Variable, Modelo


class ModeloPrueba(Modelo):

    def __init__(símismo, unid_tiempo='años', nombre='prueba'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    def incrementar(símismo, rebanada):
        super().incrementar(rebanada)

        símismo.variables.cambiar_vals({
            'Escala': símismo.variables['Escala'].obt_val() + rebanada.n_pasos,
            'Aleatorio': random.random()
        })

    @staticmethod
    def _gen_vars():
        return VariablesMod([
            Variable('Escala', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('Vacío', unid=None, ingr=True, egr=False, líms=(0, None)),
            Variable('Vacío2', unid=None, ingr=True, egr=False, líms=(0, None), inic=[0, 0]),
            Variable('Aleatorio', unid=None, ingr=False, egr=True, líms=(0, 1))
        ])

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def paralelizable(símismo):
        return True
