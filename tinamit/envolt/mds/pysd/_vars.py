from .._vars import VarConstante, VarAuxiliar, VarNivel, VarMDS, VariablesMDS


class VariablesPySD(VariablesMDS):
    pass


class VarPySD(VarMDS):
    def __init__(símismo, nombre, nombre_py, unid, ingr, egr, ec, parientes, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, ec, parientes, líms=líms, info=info)

        símismo.nombre_py = nombre_py


class VarPySDConstante(VarPySD, VarConstante):
    def __init__(símismo, nombre, nombre_py, unid, ec, parientes, líms=None, info=''):
        super().__init__(nombre, nombre_py, unid, ec, parientes, líms, info)


class VarPySDAuxiliar(VarAuxiliar, VarPySD):

    def __init__(símismo, nombre, nombre_py, unid, ec, parientes, líms=None, info=''):
        super().__init__(nombre, nombre_py, unid, ec, parientes, líms, info)


class VarPySDNivel(VarNivel, VarPySD):
    def __init__(símismo, nombre, nombre_py, unid, ec, parientes, líms=None, info=''):
        super().__init__(nombre, nombre_py, unid, ec, parientes, líms, info)
