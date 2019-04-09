from tinamit.mod import VariablesMod


class VariablesConectado(VariablesMod):

    def __init__(símismo, modelos):
        variables = [v for m in modelos for v in m.variables]
        super().__init__(variables)
