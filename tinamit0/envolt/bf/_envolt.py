from tinamit.mod import Modelo


class ModeloBF(Modelo):
    """
    La clase pariente para todos modelos biofísicos.
    """

    def __init__(símismo, variables, nombre='bf'):
        super().__init__(variables, nombre)

    @classmethod
    def prb_ingreso(cls):
        """
        Debe devolver la ubicación de un archivo de ingresos y una función que lo puede leer.

        Returns
        -------
        tuple[str, Callable]
        """

        pass

    @classmethod
    def prb_egreso(cls):
        """
        Debe devolver la ubicación de un archivo de egresos y una función que lo puede leer.

        Returns
        -------
        tuple[str, Callable]
        """

        pass

    @classmethod
    def prb_simul(cls):
        """
        Debe devolver la ubicación de un archivo de ingresos para correr una simulación de prueba.

        Returns
        -------
        str
        """
        pass

    def unidad_tiempo(símismo):
        raise NotImplementedError
