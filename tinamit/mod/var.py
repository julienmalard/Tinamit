import numpy as np

from tinamit.config import _


class VariablesMod(object):
    def __init__(símismo, variables):
        símismo.variables = {v.nombre: v for v in variables}
        if len(símismo.variables) != len(variables):
            raise ValueError(_('Los variables de un modelo deben todos tener nombre distinto.'))

    def ingresos(símismo):
        return [v for v in símismo.variables if v.ingr]

    def egresos(símismo):
        return [v for v in símismo.variables if v.egr]

    def cambiar_vals(símismo, valores):
        for vr, vl in valores.items():
            símismo[vr].poner_val(vl)

    def reinic(símismo):
        for v in símismo:
            v.reinic()

    def __getitem__(símismo, itema):
        if itema in símismo:
            return símismo.variables[str(itema)]

    def __iter__(símismo):
        for v in símismo.variables.values():
            yield v

    def __contains__(símismo, itema):
        if isinstance(itema, str):
            return itema in símismo.variables
        else:
            return itema in símismo.variables.values()


class Variable(object):
    def __init__(símismo, nombre, unid, ingr, egr, dims=(1,), líms=None, info=''):
        if not (ingr or egr):
            raise ValueError(_('Si no es variable ingreso, debe ser egreso.'))
        símismo.nombre = nombre
        símismo.unid = unid
        símismo.ingr = ingr
        símismo.egr = egr
        símismo.dims = dims
        símismo.líms = líms
        símismo.info = info

        símismo._val = np.zeros(dims)

    def poner_val(símismo, val):

        if isinstance(val, np.ndarray):
            existen = np.invert(np.isnan(val))  # No cambiamos nuevos valores que faltan
            símismo._val[existen] = val[existen]
        elif not np.isnan(val):
            símismo._val[:] = val

    def obt_val(símismo):
        return símismo._val  # para disuadir modificaciones directas a `símismo._val`

    def reinic(símismo):
        símismo._val[:] = 0

    def __str__(símismo):
        return símismo.nombre
