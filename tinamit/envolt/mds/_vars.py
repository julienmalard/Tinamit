from tinamit.mod import VariablesMod
from tinamit.mod.var import Variable


class VariablesMDS(VariablesMod):
    """
    Representa los variables de un modelo :class:`~tinamit.envolt.mds._envolt.ModeloDS`.
    """
    def auxiliares(símismo):
        return [v for v in símismo if isinstance(v, VarAuxiliar)]

    def niveles(símismo):
        return [v for v in símismo if isinstance(v, VarNivel)]

    def constantes(símismo):
        return [v for v in símismo if isinstance(v, VarConstante)]

    def parientes(símismo, var):
        return símismo[str(var)].parientes

    def hijos(símismo, var):
        return [v for v in símismo if var in v.parientes]


class VarMDS(Variable):
    """
    Un variable de un modelo :class:`~tinamit.envolt.mds._envolt.ModeloDS`.
    """
    def __init__(símismo, nombre, unid, ingr, egr, ec, parientes, inic, subs=None, líms=None, info=''):
        super().__init__(nombre, unid, ingr=ingr, egr=egr, inic=inic, líms=líms, info=info)

        símismo.ec = ec
        símismo.parientes = parientes
        símismo.subs = subs


class VarConstante(VarMDS):
    """
    Un variable constante.
    """
    def __init__(símismo, nombre, unid, ec, parientes, inic, subs=None, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms, info=info, ingr=True, egr=False
        )


class VarInic(VarMDS):
    """Un variable inicial."""
    def __init__(símismo, nombre, unid, ec, parientes, inic, subs=None, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms, info=info, ingr=True, egr=False
        )


class VarNivel(VarMDS):
    """Un variable nivel."""
    def __init__(símismo, nombre, unid, ec, parientes, inic, subs=None, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms, info=info, ingr=False, egr=True
        )
        símismo.var_inic = None

    def estab_var_inic(símismo, var_inic):
        símismo.var_inic = var_inic


class VarAuxiliar(VarMDS):
    """Un variable auxiliar."""
    def __init__(símismo, nombre, unid, ec, parientes, inic, subs=None, líms=None, info=''):
        super().__init__(
            nombre, unid, ec=ec, parientes=parientes, inic=inic, subs=subs, líms=líms, info=info, ingr=True, egr=True
        )
