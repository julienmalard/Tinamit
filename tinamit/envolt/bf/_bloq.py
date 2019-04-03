from tinamit.mod.var import Variable
from ._impac import ModeloImpaciente, VariablesModImpaciente


class ModeloBloques(ModeloImpaciente):
    pass


class VariablesModBloques(VariablesModImpaciente):
    def vars_bloque(símismo):
        return [v for v in símismo if isinstance(v, VarBloque)]

    def vars_ciclo_ingr(símismo):
        return [v for v in símismo if isinstance(v, VarBloqueIngr)]

    def vars_ciclo_egr(símismo):
        return [v for v in símismo if isinstance(v, VarBloqueEgr)]


class VarBloqueIngr(Variable):
    pass


class VarBloqueEgr(Variable):
    pass


class VarBloque(VarBloqueIngr, VarBloqueEgr):
    pass
