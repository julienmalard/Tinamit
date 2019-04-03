from tinamit.mod.var import Variable, VariablesMod
from ._envolt import EnvolturaBF


class ModeloImpaciente(EnvolturaBF):
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
