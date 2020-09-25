import random

import numpy as np

from tinamit.mod import VariablesMod, Variable, Modelo


class ModeloPrueba(Modelo):

    def __init__(símismo, unid_tiempo='años', nombre='prueba', dims=(1,)):
        símismo.unid_tiempo = unid_tiempo
        símismo.dims = dims
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    def incrementar(símismo, rebanada):
        símismo.variables.cambiar_vals({
            'Escala': símismo.variables['Escala'].obt_val() + rebanada.n_pasos,
        })

        super().incrementar(rebanada)

    def _gen_vars(símismo):
        m_inic = np.zeros(símismo.dims)
        return VariablesMod([
            Variable('Escala', unid=None, ingr=False, egr=True, inic=m_inic, líms=(0, None)),
            Variable('Vacío', unid=None, ingr=True, egr=False, inic=m_inic, líms=(0, None)),
            Variable('Vacío2', unid=None, ingr=True, egr=False, líms=(0, None), inic=[0, 0]),
        ])

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def paralelizable(símismo):
        return True


class ModeloAlea(Modelo):

    def __init__(símismo, unid_tiempo='años', nombre='alea'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    def incrementar(símismo, rebanada):
        símismo.variables.cambiar_vals({
            'Escala': símismo.variables['Escala'].obt_val() + rebanada.n_pasos,
            'Aleatorio': random.random()
        })

        super().incrementar(rebanada)

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
