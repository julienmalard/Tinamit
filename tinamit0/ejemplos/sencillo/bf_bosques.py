import random

import numpy as np

from tinamit.envolt.bf import ModeloBF
from tinamit.mod import VariablesMod, Variable


class PruebaBF(ModeloBF):

    def __init__(símismo, dims_bosques=(1,)):
        vars_ = VariablesMod([
            Variable('Lluvia', unid='m3/mes', ingr=False, egr=True, inic=1, líms=(0, None)),
            Variable('Bosques', unid='m2', ingr=True, egr=False, inic=np.full(dims_bosques, 1e6), líms=(0, None)),
        ])
        super().__init__(variables=vars_)

    def incrementar(símismo, rebanada):
        bosques = símismo.variables['Bosques'].obt_val()

        símismo.variables['Lluvia'].poner_val(random.random() * min(1, np.mean(bosques) / 9e5) ** 5 * rebanada.n_pasos)
        super().incrementar(rebanada)

    def unidad_tiempo(símismo):
        return 'meses'

    def paralelizable(símismo):
        return True
