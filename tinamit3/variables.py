from typing import List, Optional, Dict


class Variable(object):
    def __init__(
            símismo, nombre: str, unids: Optional[str],
            coords: Optional[Dict] = None,
            dims: Optional[List] = None
    ):
        símismo.nombre = nombre
        símismo.unids = unids
        símismo.coords = coords or {}
        símismo.dims = dims or []
