from numbers import Number
from typing import Callable

from .transformador import Transformador


class Conv(Transformador):
    def __init__(símismo, f: Callable[[Number], Number]):
        super().__init__(f=lambda x: x.apply(f))


class FactorConv(Transformador):
    def __init__(símismo, factor: Number):
        super().__init__(f=lambda x: x * factor)
