from ...mod import Modelo


class ModeloDS(Modelo):
    ext = []

    def __init__(símismo, variables, nombre='mds'):
        super().__init__(variables, nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError
