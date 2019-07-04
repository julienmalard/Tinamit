from tinamit.config import _
from .res import ResultadosSimul
from .var import Variable


class VariablesMod(object):

    def __init__(símismo, variables):
        símismo.variables = {v.nombre: v for v in variables}
        if len(símismo.variables) != len(variables):
            raise ValueError(_('Los variables de un modelo deben todos tener nombre distinto.'))

    def ingresos(símismo):
        return [v for v in símismo if v.ingr]

    def egresos(símismo):
        return [v for v in símismo if v.egr]

    def cambiar_vals(símismo, valores):
        for vr, vl in valores.items():
            símismo[vr].poner_val(vl)

    def reinic(símismo):
        for v in símismo:
            v.reinic()

    def gen_res(símismo, nombre, t, vars_interés):
        return ResultadosSimul(nombre=nombre, t=t, vars_interés=símismo._resolver_vars(vars_interés))

    def _resolver_vars(símismo, l_vars):
        if isinstance(l_vars, (Variable, str)):
            l_vars = [l_vars]
        return [símismo[v] for v in l_vars] if l_vars is not None else list(símismo)

    def __getitem__(símismo, itema):
        if itema in símismo:
            return símismo.variables[str(itema)]
        raise KeyError(itema)

    def __setitem__(símismo, llave, valor):
        símismo.variables[llave] = valor

    def __iter__(símismo):
        for v in símismo.variables.values():
            yield v

    def __contains__(símismo, itema):
        if isinstance(itema, str):
            return itema in símismo.variables
        else:
            return itema in símismo.variables.values()
