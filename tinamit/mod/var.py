import numpy as np

from tinamit.config import _


class Variable(object):
    """La clase más general para variables de modelos en Tinamït."""

    def __init__(símismo, nombre, unid, ingr, egr, inic=0, líms=None, info=''):
        """

        Parameters
        ----------
        nombre: str
            El nombre del variable.
        unid: str or None
            Las unidades del variable.
        ingr: bool
            Si es un ingreso al modelo.
        egr: bool
            Si es un egreso del modelo.
        inic: int or float or np.ndarray
            El valor inicial del modelo.
        líms: tuple
            Los límites del variable.
        info: str
            Descripción detallada del variable.
        """
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

        símismo._val = símismo.inic.astype(float)

    def poner_val(símismo, val):
        """
        Establece el valor del variable.

        Parameters
        ----------
        val: int or float or np.ndarray
            El nuevo valor.

        """

        if isinstance(val, np.ndarray):
            existen = np.invert(np.isnan(val))  # No cambiamos nuevos valores que faltan
            símismo._val[existen] = val[existen]
        elif not np.isnan(val):
            símismo._val[:] = val

    def obt_val(símismo):
        """
        Devuelve el valor del variable.
        """
        return símismo._val  # para disuadir modificaciones directas a `símismo._val`

    def reinic(símismo):
        """
        Reinicializa el variable a su valor pre-simulación.
        """
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
        return -np.inf if líms[0] is None else líms[0], np.inf if líms[1] is None else líms[1]
