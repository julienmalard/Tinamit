

class Modelo(object):
    def __init__(símismo, nombre):
        símismo.nombre = nombre
        símismo.variables = {}

    def sacar_vars(símismo):
        # para hacer: verificar este
        return [v for v in símismo.variables]

    def iniciar_modelo(símismo):
        raise NotImplementedError

    def incrementar(símismo, paso):
        """

        :param paso:
        :type paso: int

        """

        raise NotImplementedError

    def leer_vals(símismo):
        raise NotImplementedError

    def cambiar_vals(símismo, valores):
        """

        :param valores:
        :type valores: dict

        """
        raise NotImplementedError
