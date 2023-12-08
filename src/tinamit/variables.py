from __future__ import annotations

from typing import Optional, Dict, List, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .modelo import Modelo


class Variable(object):
    def __init__(
            símismo,
            nombre: str,
            unids: Optional[str],
            ingreso: bool, egreso: bool,
            modelo: Union[Modelo, str],
            coords: Optional[Dict] = None,
            dims: Optional[List] = None
    ):
        símismo.nombre = nombre
        símismo.unids = unids
        símismo.ingreso = ingreso
        símismo.egreso = egreso
        símismo.modelo = str(modelo)
        símismo.coords = coords or {}
        símismo.dims = dims or []

    def __str__(símismo):
        return símismo.nombre
