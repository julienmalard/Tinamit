from tinamit.mod.var import VariablesMod, Variable


class VariablesMDS(VariablesMod):
    def auxiliares(símismo):
        return [v for v in símismo if isinstance(v, VarAuxiliar)]

    def niveles(símismo):
        return [v for v in símismo if isinstance(v, VarNivel)]

    def constantes(símismo):
        return [v for v in símismo if isinstance(v, VarConstante)]

    def hijos(símismo, var):
        return símismo[str(var)].hijos()

    def parientes(símismo, var):
        return [v for v in símismo if var in v.hijos()]


class VariableMDS(Variable):
    def __init__(símismo, nombre, unid, ingr, egr, ec, hijos, parientes, líms=None, info=''):
        super().__init__(nombre, unid, ingr=ingr, egr=egr, líms=líms, info=info)

        símismo.ec = ec
        símismo.hijos = hijos
        símismo.parientes = parientes


class VarConstante(VariableMDS):
    def __init__(símismo, nombre, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, hijos=hijos, parientes=parientes, líms=líms, info=info, ingr=True, egr=False
        )


class VarInic(VariableMDS):
    def __init__(símismo, nombre, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, hijos=hijos, parientes=parientes, líms=líms, info=info, ingr=True, egr=False
        )


class VarNivel(VariableMDS):
    def __init__(símismo, nombre, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, hijos=hijos, parientes=parientes, líms=líms, info=info, ingr=False, egr=True
        )


class VarAuxiliar(VariableMDS):
    def __init__(símismo, nombre, unid, ec, hijos, parientes, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, hijos=hijos, parientes=parientes, líms=líms, info=info, ingr=True, egr=True
        )
