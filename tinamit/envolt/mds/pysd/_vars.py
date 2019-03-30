from tinamit.envolt.mds import VarConstante, VarAuxiliar, VarNivel, VariableMDS


class VarPySD(VariableMDS):
    def __init__(símismo, nombre, nombre_py, unid, ingr, egr, ec, hijos, parientes, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, ec, hijos, parientes, líms=líms, info=info)

        símismo.nombre_py = nombre_py


class VarPySDConstante(VarPySD, VarConstante):
    def __init__(símismo, nombre, nombre_py, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(nombre, nombre_py, unid, ec, hijos, parientes, líms, info)


class VarPySDAuxiliar(VarAuxiliar, VarPySD):

    def __init__(símismo, nombre, nombre_py, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(nombre, nombre_py, unid, ec, hijos, parientes, líms, info)


class VarPySDNivel(VarNivel, VarPySD):
    def __init__(símismo, nombre, nombre_py, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(nombre, nombre_py, unid, ec, hijos, parientes, líms, info)
