from tinamit.mod import Variable, VariablesMod


class VariablesConectado(VariablesMod):

    pass


class VarConectado(Variable):
    def __init__(símismo, base):
        símismo.base = base
        super().__init__(base.nombre, base.unid, base.ingr, base.egr, base.líms, base.info)
