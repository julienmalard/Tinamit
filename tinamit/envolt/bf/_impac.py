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

    def cambiar_vals(símismo, valores):

    def iniciar_modelo(símismo, corrida):

    def incrementar(símismo, corrida):
        pass


class VariablesModImpaciente(VariablesMod):
    def vars_ciclo(símismo):
        return [v for v in símismo if isinstance(v, VarCiclo)]

    def vars_ciclo_ingr(símismo):
        return [v for v in símismo if isinstance(v, VarCicloIngr)]

    def vars_ciclo_egr(símismo):
        return [v for v in símismo if isinstance(v, VarCicloEgr)]


class VarCicloIngr(Variable):
    pass


class VarCicloEgr(Variable):
    pass


class VarCiclo(VarCicloIngr, VarCicloEgr):
    pass
