from tinamit.mod import Variable, VariablesMod


class VariablesConectado(VariablesMod):

    def __init__(símismo, modelos):
        variables = [v for m in modelos for v in m.variables]
        super().__init__(variables)


class VarConectado(Variable):
    def __init__(símismo, base):
        símismo.base = base
        super().__init__(base.nombre, base.unid, base.ingr, base.egr, base.líms, base.info)
