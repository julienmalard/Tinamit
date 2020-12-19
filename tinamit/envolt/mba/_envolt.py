from ...mod import Modelo


class ModeloBA(Modelo):

    def __init__(símismo, variables, nombre='mba'):
        super().__init__(variables, nombre=nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError
