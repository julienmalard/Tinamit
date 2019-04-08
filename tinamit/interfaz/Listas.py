import tkinter as tk

from tinamit.interfaz import Formatos as Fms


class ConecciónVar(object):
    def __init__(símismo, pariente, var1, var2, multiplicador):
        símismo.var1 = var1
        símismo.var2 = var2
        símismo.multiplicador = multiplicador
        símismo.caja = tk.Frame(pariente, **Fms.formato_cajas)

        símismo.botón_quitar = BotónQuitarConección(símismo)
        símismo.botón_editar = BotónEditarConección(símismo)


class BotónQuitarConección(object):
    pass


class BotónEditarConección(object):
    pass


class Lengua(object):
    def __init__(símismo):
        pass
