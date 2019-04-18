from ...mod import Modelo


class EnvolturaBF(Modelo):

    def __init__(símismo, variables, nombre='bf'):
        super().__init__(variables, nombre)

    def iniciar_modelo(símismo, corrida):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def incrementar(símismo, corrida):
        raise NotImplementedError
