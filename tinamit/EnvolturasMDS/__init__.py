import os

from tinamit import _
from tinamit.EnvolturasMDS.PySD import ModeloPySD
from tinamit.EnvolturasMDS.Vensim import ModeloVensim, ModeloVensimMdl

dic_motores = {
    '.vpm': [ModeloVensim],
    '.mdl': [ModeloPySD, ModeloVensimMdl],
    '.xml': [ModeloPySD],
    '.xmile': [ModeloPySD]

    # Agregar otros tipos de modelos DS aquí.

}


def generar_mds(archivo, motor=None):
    """
    Esta función genera una instancia de modelo de DS. Identifica el tipo de archivo por su extensión (p. ej., .vpm) y
    después genera una instancia de la subclase apropiada de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS`.

    :param archivo: El archivo del modelo DS.
    :type archivo: str

    :return: Un modelo DS.
    :rtype: EnvolturaMDS

    """

    # Identificar la extensión.
    ext = os.path.splitext(archivo)[1]

    # Verificar si podemos leer este tipo de archivo.
    if ext not in dic_motores:
        # Mensaje para modelos todavía no incluidos en Tinamit.
        raise ValueError(_('El tipo de modelo "{}" no se acepta como modelo DS en Tinamit al momento. Si piensas'
                           'que podrías contribuir aquí, ¡contáctenos!').format(ext))
    else:
        errores = {}
        if motor is None:
            motores_potenciales = dic_motores[ext]
        else:
            if not isinstance(motor, list):
                motor = [motor]
            motores_potenciales = [x for x in dic_motores[ext] if x in motor]

        for env in motores_potenciales:
            try:
                return env(archivo)
            except BaseException as e:
                errores[env.__name__] = e

        raise ValueError(_('El modelo "{}" no se pudo leer. Intentamos las envolturas siguientes, pero no funcionaron:'
                           '{}').format(archivo, ''.join(['\n\t{}: {}'.format(env, e) for env, e in errores.items()])))
