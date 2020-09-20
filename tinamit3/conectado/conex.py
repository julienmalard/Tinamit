from numbers import Number
from typing import Union, Optional, Callable

from tinamit.mod import Modelo
from tinamit3.variables import Variable


class Conex(object):
    def __init__(
            símismo,
            de: Union[str, Variable],
            a: Union[str, Variable],
            modelo_de: Union[str, Modelo],
            modelo_a: Union[str, Modelo],
            conv: Number = 1,
            transf: Optional[Callable] = None
    ):
        símismo.de = str(de)
        símismo.a = str(a)

        símismo.modelo_de = str(modelo_de)
        símismo.modelo_a = str(modelo_a)

        símismo.conv = conv
        símismo.transf = transf
