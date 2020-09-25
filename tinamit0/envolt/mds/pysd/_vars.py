from .._vars import VarConstante, VarAuxiliar, VarNivel, VarMDS, VariablesMDS


class VariablesPySD(VariablesMDS):
    pass


class VarPySD(VarMDS):
    def __init__(símismo, nombre_py, **args_ll):
        símismo.nombre_py = nombre_py
        super().__init__(**args_ll)


class VarPySDConstante(VarPySD, VarConstante):
    def __init__(símismo, nombre, nombre_py, unid, ec, parientes, inic=0, subs=None, líms=None, info=''):
        super().__init__(
            nombre_py, nombre=nombre, unid=unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms,
            info=info
        )


class VarPySDAuxiliar(VarPySD, VarAuxiliar):

    def __init__(símismo, nombre, nombre_py, unid, ec, parientes, inic=0, subs=None, líms=None, info=''):
        super().__init__(
            nombre_py, nombre=nombre, unid=unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms,
            info=info
        )


class VarPySDNivel(VarPySD, VarNivel):
    def __init__(símismo, nombre, nombre_py, unid, ec, parientes, inic=0, subs=None, líms=None, info=''):
        super().__init__(
            nombre_py, nombre=nombre, unid=unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms,
            info=info
        )
