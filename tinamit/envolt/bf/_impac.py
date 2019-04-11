from tinamit.mod.var import Variable, VariablesMod
from ._envolt import EnvolturaBF


class ModeloImpaciente(EnvolturaBF):

    def __init__(símismo, nombre='bf'):
        símismo.paso_en_ciclo = 0
        símismo.tmñ_ciclo = 1

        super().__init__(nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def _gen_vars(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo, corrida):
        símismo.paso_en_ciclo = 0
        super().iniciar_modelo(corrida)

    def incrementar(símismo, corrida):
        raise NotImplementedError


class VariablesModImpaciente(VariablesMod):
    def vars_ciclo(símismo):
        return [v for v in símismo if isinstance(v, VarCiclo)]

    def act_paso(símismo, paso):
        for v in símismo.vars_ciclo():
            v.act_paso(paso=paso)


class VarCiclo(Variable):

    def __init__(símismo, nombre, unid, ingr, egr, dims=(1,), líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, dims, líms, info)
        símismo._matr_paso = None
        símismo.paso = 0

    def poner_val(símismo, val):
        símismo._matr_paso[símismo.paso] = val
        super().poner_val(val)

    def poner_vals_ciclo(símismo, val):
        símismo._matr_paso[:] = val

    def obt_vals_ciclo(símismo):
        return símismo._matr_paso[símismo.paso]

    def act_paso(símismo, paso):
        símismo.paso = paso
        super().poner_val(símismo._matr_paso[paso])

    def reinic(símismo):
        símismo.paso = 0
        super().reinic()



