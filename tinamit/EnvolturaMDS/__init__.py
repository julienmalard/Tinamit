import os

from tinamit.EnvolturaMDS.Vensim import ModeloVensim, ModeloVensimMdl


def generar_mds(archivo):
    """
    Esta función genera una instancia de modelo de DS. Identifica el tipo de archivo por su extensión (p. ej., .vpm) y
    después genera una instancia de la subclase apropiada de :class:`~tinamit.EnvolturaMDS.EnvolturaMDS`.

    :param archivo: El archivo del modelo DS.
    :type archivo: str

    :return: Un modelo DS.
    :rtype: tinamit.MDS.EnvolturaMDS

    """

    # Identificar la extensión.
    ext = os.path.splitext(archivo)[1]

    # Crear la instancia de modelo apropiada para la extensión del archivo.
    if ext == '.vpm':
        # Modelos VENSIM
        return ModeloVensim(archivo)
    if ext == '.mdl':
        return ModeloVensimMdl(archivo)
    else:
        # Agregar otros tipos de modelos DS aquí.

        # Mensaje para modelos todavía no incluidos en Tinamit.
        raise ValueError('El tipo de modelo "{}" no se acepta como modelo DS en Tinamit al momento. Si piensas'
                         'que podrías contribuir aquí, ¡contáctenos!'.format(ext))
