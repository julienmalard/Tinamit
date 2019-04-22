import numpy as np

from tinamit.config import _


class Variable(object):
    def __init__(símismo, nombre, unid, ingr, egr, inic=0, líms=None, info=''):
        if not (ingr or egr):
            raise ValueError(_('Si no es variable ingreso, debe ser egreso.'))
        símismo.nombre = nombre
        símismo.unid = unid
        símismo.ingr = ingr
        símismo.egr = egr
        símismo.inic = _a_np(inic)
        símismo.dims = símismo.inic.shape
        símismo.líms = _proc_líms(líms)
        símismo.info = info

        símismo._val = símismo.inic.copy()

    def poner_val(símismo, val):

        if isinstance(val, np.ndarray):
            existen = np.invert(np.isnan(val))  # No cambiamos nuevos valores que faltan
            símismo._val[existen] = val[existen]
        elif not np.isnan(val):
            símismo._val[:] = val

    def obt_val(símismo):
        return símismo._val  # para disuadir modificaciones directas a `símismo._val`

    def reinic(símismo):
        símismo._val[:] = símismo.inic

    def __iadd__(símismo, otro):
        símismo.poner_val(símismo._val + otro)
        return símismo

    def __imul__(símismo, otro):
        símismo.poner_val(símismo._val * otro)

    def __imod__(símismo, otro):
        símismo.poner_val(símismo._val % otro)

    def __ifloordiv__(símismo, otro):
        símismo.poner_val(símismo._val // otro)

    def __ipow__(símismo, otro):
        símismo.poner_val(símismo._val ** otro)

    def __str__(símismo):
        return símismo.nombre


def _a_np(val):
    if isinstance(val, np.ndarray):
        return val
    elif isinstance(val, (int, float, np.number)):
        return np.array([val])
    else:
        return np.array(val)


def _proc_líms(líms):
    if líms is None:
        return -np.inf, np.inf
    else:
        return líms[0] or -np.nan, líms[1] or np.nan
