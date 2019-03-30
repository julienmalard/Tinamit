from tinamit import Modelo


class EnvolturaBF(Modelo):
    def __init__(símismo, nombre='bf'):
        super().__init__(nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar_modelo(símismo):
        raise NotImplementedError
