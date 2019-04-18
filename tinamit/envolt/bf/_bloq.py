import numpy as np

from tinamit.envolt.bf._deter import ModeloDeterminado
from tinamit.mod.var import Variable
from ._impac import VariablesModImpaciente


class ModeloBloques(ModeloDeterminado):

    def __init__(símismo, tmñ_bloques, variables, nombre='bf'):
        super().__init__(tmñ_ciclo=np.sum(tmñ_bloques), variables=variables, nombre=nombre)

        símismo.tmñ_bloques = tmñ_bloques

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError


class VariablesModBloques(VariablesModImpaciente):

    def __init__(símismo, variables, tmñ_bloques):
        símismo.tmñ_bloques_cum = np.cumsum(tmñ_bloques)
        símismo.n_bloques = len(tmñ_bloques)
        super().__init__(variables)

    def act_paso(símismo, paso):
        b = next(i for i, s in enumerate(símismo.tmñ_bloques_cum) if paso < s)
        for v in símismo.vars_bloque():
            v.act_paso(bloque=b)
        super().act_paso(paso)

    def vars_bloque(símismo):
        return [v for v in símismo if isinstance(v, VarBloque)]


class VarBloque(Variable):

    def __init__(símismo, nombre, unid, ingr, egr, dims=(1,), líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, dims, líms, info)

    def poner_val(símismo, val):
        pass

    def obt_val(símismo):
        pass

    def act_paso(símismo, bloque):
        pass

    def reinic(símismo):
        pass
