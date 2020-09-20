from typing import Optional, Dict, List

from tinamit3.variables import Variable


class VariablePySD(Variable):
    def __init__(
            símismo, nombre: str, unids: Optional[str], nombre_pysd: str,
            coords: Optional[Dict] = None,
            dims: Optional[List] = None
    ):
        símismo.nombre_pysd = nombre_pysd
        super().__init__(nombre, unids, coords, dims)
