from numbers import Number
from typing import Union, Optional

from fnt.tinamit3.modelo import Modelo
from fnt.tinamit3.resultados import FactorConv, Transformador
from fnt.tinamit3.variables import Variable


class ConexiónVars(object):
    def __init__(
            símismo,
            de: Union[str, Variable],
            a: Union[str, Variable],
            modelo_de: Union[str, Modelo],
            modelo_a: Union[str, Modelo],
            transf: Optional[Union[Transformador, Number]] = None,
            integ_tiempo: str = "mean"
    ):
        símismo.de = str(de)
        símismo.a = str(a)

        símismo.modelo_de = str(modelo_de)
        símismo.modelo_a = str(modelo_a)

        if not isinstance(transf, Transformador):
            transf = FactorConv(transf)

        símismo.transf: Optional[Transformador] = transf

        símismo.integ_tiempo = integ_tiempo
