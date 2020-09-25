from fnt.tinamit3.modelo import Modelo


class Externos(Modelo):
    def __init__(símismo, iniciales=None, temporales=None):
        símismo.iniciales = iniciales or []
        símismo.temporales = temporales or {}


def gen_externos(externos):
    if externos is None:
        return