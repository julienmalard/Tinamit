import os

from tinamit.Modelo import Modelo


class ModeloMDS(Modelo):
    """

    """

    def __init__(símismo):
        """

        """
        super().__init__(nombre='mds')

    def cambiar_vals(símismo, valores):
        raise NotImplementedError

    def incrementar(símismo, paso):
        raise NotImplementedError

    def leer_vals(símismo):
        raise NotImplementedError

    def iniciar_modelo(símismo):
        raise NotImplementedError


class ModeloVENSIM(ModeloMDS):
    """

    """

    def __init__(símismo, archivo):

        super().__init__()

    def cambiar_vals(símismo, valores):
        pass

    def incrementar(símismo, paso):
        pass

    def leer_vals(símismo):
        pass

    def iniciar_modelo(símismo):
        pass


def generar_mds(archivo):
    """

    :param archivo:
    :type archivo: str

    :return:
    :rtype: ModeloMDS

    """

    ext = os.path.splitext(archivo)[1]

    if ext == '.vpm':
        return ModeloVENSIM(archivo)
    else:
        raise ValueError('El tipo de modelo {} no se acepta como modelo DS en Tinamit, al momento. Si piensas'
                         'que podrías contribuir aquí, ¡contáctenos!'.format(ext))
