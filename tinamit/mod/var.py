from tinamit.config import _


class VariablesMod(object):
    def __init__(símismo, variables):
        símismo.variables = {v: v.nombre for v in variables}

    def ingresos(símismo):
        return [v for v in símismo.variables if v.ingr]

    def egresos(símismo):
        return [v for v in símismo.variables if v.egr]

    def __getitem__(símismo, itema):
        return símismo.variables[itema]

    def __iter__(símismo):
        for v in símismo.variables.values():
            yield v

    def __contains__(símismo, itema):
        return str(itema) in símismo.variables


class Variable(object):
    def __init__(símismo, nombre, unid, ingr, egr, líms=None, info=''):
        if not (ingr or egr):
            raise ValueError(_('Si no es variable ingreso, debe ser egreso.'))
        símismo.nombre = nombre
        símismo.unid = unid
        símismo.ingr = ingr
        símismo.egr = egr
        símismo.líms = líms
        símismo.info = info
