import numpy as np
from tinamit.mod import VariablesMod
from tinamit.mod.var import Variable


class VariablesMBA(VariablesMod):
    """
    Representa los variables de un modelo :class:`~tinamit.envolt.mba.ModeloBA`.
    """

    def __init__(símismo, variables):
        no_mds = [vr for vr in variables if not isinstance(vr, VarMBA)]
        if no_mds:
            raise TypeError('Variables {vrs} deben ser de tipo ``VarMBA``.'.format(vrs=', '.join(no_mds)))
        super().__init__(variables)


class VarMBA(Variable):
    """
    Un variable de un modelo :class:`~tinamit.envolt.mds.ModeloDS`.
    """

    def __init__(símismo, nombre, unid, ingr, egr, inic, líms=None, info=''):
        super().__init__(nombre, unid, ingr=ingr, egr=egr, inic=inic, líms=líms, info=info)


class VarAgenteMBA(VarMBA):
    def __init__(símismo, nombre, unid, inic, líms=None, info=''):
        super().__init__(nombre, unid, ingr=True, egr=False, inic=inic, líms=líms, info=info)


class VarCuadMBA(VarMBA):
    def __init__(símismo, nombre, unid, inic, líms=None, info='', f_agreg=np.sum):
        super().__init__(nombre, unid, ingr=True, egr=False, inic=inic, líms=líms, info=info)
        símismo.f_agreg = f_agreg
