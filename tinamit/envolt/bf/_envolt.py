from tinamit.mod import Modelo


class ModeloBF(Modelo):

    def __init__(símismo, variables, nombre='bf'):
        super().__init__(variables, nombre)

    @classmethod
    def prb_ingreso(cls):
        pass

    @classmethod
    def prb_egreso(cls):
        pass

    @classmethod
    def prb_simul(cls):
        pass

    def unidad_tiempo(símismo):
        raise NotImplementedError
