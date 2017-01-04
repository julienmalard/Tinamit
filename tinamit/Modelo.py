

class Modelo(object):
    """

    """
    def __init__(símismo, nombre):
        """

        :param nombre:
        :type nombre: str

        """

        # El nombre del modelo (sirve como una referencia a este modelo en el modelo conectado).
        símismo.nombre = nombre

        # El diccionario de variables necesita la forma siguiente. Se llena con la función símismo.obt_vars().
        # {var1: {'val': 13, 'unidades': cm, 'ingreso': True, 'egreso': True},
        #  var2: {...},
        #  ...}
        símismo.variables = {}

        #
        símismo.vars_saliendo = []
        símismo.vars_entrando = []

    def inic_vars(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        """

        :param tiempo_final:
        :type tiempo_final:
        :param nombre_corrida:
        :type nombre_corrida:
        """

        raise NotImplementedError

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso: int

        """
        raise NotImplementedError

    def leer_vals(símismo):
        """

        """
        raise NotImplementedError

    def cambiar_vals(símismo, valores):
        """

        :param valores:
        :type valores: dict

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """

        """
        raise  NotImplementedError
