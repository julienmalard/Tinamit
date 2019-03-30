from tinamit.mod.var import Variable, VariablesMod
from ._envolt import EnvolturaBF


class ModeloImpaciente(EnvolturaBF):
    pass


class VariablesModImpaciente(VariablesMod):
    pass


class VarIngrCiclo(Variable):
    pass


class VarEgrCiclo(Variable):
    pass


class VarCiclo(VarIngrCiclo, VarEgrCiclo):
    pass
