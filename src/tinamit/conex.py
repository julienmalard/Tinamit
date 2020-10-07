from __future__ import annotations

from numbers import Number
from typing import TYPE_CHECKING, Type, Callable
from typing import Union, Optional

from .hilo import RequísitoContemporáneo, RequísitoInicPaso, Requísito
from .resultados import FactorConv, Transformador
from .variables import Variable

if TYPE_CHECKING:
    from .modelo import Modelo


class ConexiónVars(object):
    clase_requísito: Type[Requísito] = RequísitoInicPaso

    def __init__(
            símismo,
            de: Union[str, Variable],
            a: Union[str, Variable],
            modelo_de: Union[str, Modelo],
            modelo_a: Union[str, Modelo],
            transf: Optional[Union[Transformador, Number]] = None,
            integ_tiempo: Union[str, Callable] = "last"
    ):
        símismo.de = str(de)
        símismo.a = str(a)

        símismo.modelo_de = str(modelo_de)
        símismo.modelo_a = str(modelo_a)

        if transf is not None and not isinstance(transf, Transformador):
            transf = FactorConv(transf)

        símismo.transf: Optional[Transformador] = transf

        símismo.integ_tiempo = integ_tiempo


class ConexiónVarsContemporánea(ConexiónVars):
    clase_requísito = RequísitoContemporáneo
