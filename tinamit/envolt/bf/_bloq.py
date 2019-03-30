from tinamit.mod.var import Variable, VariablesMod
from ._impac import ModeloImpaciente


class ModeloBloques(ModeloImpaciente):
    pass


class VariablesModBloques(VariablesMod):
    pass


class VarIngrBloque(Variable):
    pass


class VarEgrBloque(Variable):
    pass


class VarBloque(VarIngrBloque, VarEgrBloque):
    pass
