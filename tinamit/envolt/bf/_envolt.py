from tinamit import Modelo


class EnvolturaBF(Modelo):
    leng_orig = 'en'

    def __init__(símismo, variables, nombre='bf'):
        super().__init__(variables, nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError
