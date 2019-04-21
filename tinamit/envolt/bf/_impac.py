import numpy as np

from tinamit.mod.var import Variable, VariablesMod
from ._envolt import EnvolturaBF


class ModeloImpaciente(EnvolturaBF):

    def __init__(símismo, tmñ_ciclo, variables, nombre='bf'):
        símismo.paso_en_ciclo = tmñ_ciclo - 1
        símismo.tmñ_ciclo = tmñ_ciclo

        super().__init__(variables, nombre)

    def iniciar_modelo(símismo, corrida):
        símismo.paso_en_ciclo = símismo.tmñ_ciclo - 1
        super().iniciar_modelo(corrida)

    def unidad_tiempo(símismo):
        raise NotImplementedError


class VariablesModImpaciente(VariablesMod):
    def vars_paso(símismo):
        return [v for v in símismo if isinstance(v, VarPaso)]

    def act_paso(símismo, paso):
        for v in símismo.vars_paso():
            v.act_paso(paso=paso)


class VarPaso(Variable):

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_ciclo, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, inic=inic, líms=líms, info=info)
        símismo._matr_paso = np.zeros((tmñ_ciclo, *símismo._val.shape))
        símismo._matr_paso[:] = símismo.inic
        símismo.paso = 0

    def poner_val(símismo, val):
        símismo._matr_paso[símismo.paso] = val
        super().poner_val(val)

    def obt_val(símismo):
        return símismo._matr_paso[símismo.paso]

    def poner_vals_paso(símismo, val):
        símismo._matr_paso[:] = val.reshape(*símismo._matr_paso.shape)  # reformar para variables unidimensionales

    def obt_vals_paso(símismo):
        return símismo._matr_paso

    def act_paso(símismo, paso):
        símismo.paso = paso
        super().poner_val(símismo._matr_paso[paso])

    def reinic(símismo):
        símismo.paso = 0
        símismo._matr_paso[:] = símismo.inic
        super().reinic()
