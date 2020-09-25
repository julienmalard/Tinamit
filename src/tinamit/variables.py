from __future__ import annotations

from typing import Optional, Dict, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .modelo import Modelo


class Variable(object):
    def __init__(
            símismo,
            nombre: str,
            unids: Optional[str],
            ingreso: bool, egreso: bool,
            modelo: Modelo,
            coords: Optional[Dict] = None,
            dims: Optional[List] = None
    ):
        símismo.nombre = nombre
        símismo.unids = unids
        símismo.ingreso = ingreso
        símismo.egreso = egreso
        símismo.modelo = modelo
        símismo.coords = coords or {}
        símismo.dims = dims or []
