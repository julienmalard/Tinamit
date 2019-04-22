from tinamit.mod import Modelo


class EnvolturaBF(Modelo):

    def __init__(símismo, variables, nombre='bf'):
        super().__init__(variables, nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError
