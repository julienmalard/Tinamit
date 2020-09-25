from tinamit.config import _
from ._res import ResultadosConectado
from ..mod import VariablesMod


class VariablesConectado(VariablesMod):

    def __init__(símismo, modelos):
        super().__init__(variables=[])
        símismo.modelos = modelos
        símismo.variables = {str(m): m.variables for m in modelos}

    def gen_res(símismo, nombre, t, vars_interés):
        return ResultadosConectado(
            nombre=nombre, t=t, modelos=símismo.modelos, vars_interés=símismo._resolver_vars(vars_interés)
        )

    def _resolver(símismo, var):
        try:
            return next((m, v_m[var]) for m, v_m in símismo.variables.items() if var in v_m)
        except StopIteration:
            raise KeyError(_('Variable {var} no existe.').format(var))

    def __getitem__(símismo, itema):
        mod, var = símismo._resolver(itema)
        return símismo.variables[mod][var]

    def __setitem__(símismo, llave, valor):
        mod, var = símismo._resolver(llave)
        símismo.variables[mod][var] = valor

    def __iter__(símismo):
        for m, v_m in símismo.variables.items():
            for v in v_m:
                yield v

    def __contains__(símismo, itema):
        try:
            símismo._resolver(itema)
            return True
        except KeyError:
            return False
