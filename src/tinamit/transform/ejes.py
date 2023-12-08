from typing import Dict

from .transformador import Transformador


class RenombrarEjes(Transformador):
    def __init__(símismo, dic_nombres: Dict[str, str]):
        super().__init__(f=lambda x: x.rename_dims(dic_nombres))

class CombinarEjes(Transformador):
    pass
