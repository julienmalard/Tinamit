from tinamit.mod.var import Variable, VariablesMod
from ._envolt import EnvolturaBF


class ModeloImpaciente(EnvolturaBF):

    def __init__(símismo, nombre='bf'):
        símismo.paso_en_ciclo = 0
        símismo.ciclo = 0
        símismo.tmñ_ciclo = 1

        super().__init__(nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def _gen_vars(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo, corrida):
        símismo.paso_en_ciclo = símismo.ciclo = 0
        super().iniciar_modelo(corrida)

    def incrementar(símismo, corrida):
        pass


class VariablesModImpaciente(VariablesMod):
    def vars_ciclo(símismo):
        return [v for v in símismo if isinstance(v, VarCiclo)]

    def vars_ciclo_ingr(símismo):
        return [v for v in símismo if isinstance(v, VarCicloIngr)]

    def vars_ciclo_egr(símismo):
        return [v for v in símismo if isinstance(v, VarCicloEgr)]

    def act_paso(símismo, paso):
        for v in símismo:
            if isinstance(v, PlantillaVarCiclo)):
                v.act_paso(paso=paso)


class PlantillaVarCiclo(Variable):

    def __init__(símismo, nombre, unid, ingr, egr, dims=(1,), líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, dims, líms, info)
        símismo.paso = 0

    def act_paso(símismo, paso):
        raise NotImplementedError


class VarCicloIngr(PlantillaVarCiclo):

    def __init__(símismo, nombre, unid, ingr, egr, dims=(1,), líms=None, info=''):
        símismo._matr_ingr_paso =
        super().__init__(nombre, unid, ingr, egr, dims, líms, info)

    def poner_val(símismo, val):
        símismo._matr_ingr_paso[símismo.paso] = val
        super().poner_val(val)

    def act_paso(símismo, paso):
        símismo.paso = paso
        super().poner_val(símismo._matr_ingr_paso[paso])


class VarCicloEgr(PlantillaVarCiclo):


    def obt_val(símismo):
        return símismo._matr_egr_paso[símismo.paso]


class VarCiclo(Variable):
    def __init__(símismo, nombre, unid, ingr, egr, dims=(1,), líms=None, info=''):
        símismo._matr_egr_paso =
        super().__init__(nombre, unid, ingr, egr, dims, líms, info)

