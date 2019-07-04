from .._vars import VarAuxiliar, VariablesMDS


class VariablesModVensimDLL(VariablesMDS):
    def editables(símismo):
        return [v for v in símismo if isinstance(v, VarAuxEditable)]

    def no_editables(símismo):
        return [v for v in símismo if not isinstance(v, VarAuxEditable)]


class VarAuxEditable(VarAuxiliar):
    pass
