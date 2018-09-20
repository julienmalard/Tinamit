import os

from tinamit.EnvolturasMDS.PySD import ModeloPySD
from tinamit.EnvolturasMDS.Vensim import ModeloVensim
from tinamit.MDS import EnvolturaMDS
from tinamit.config import _
from tinamit.cositas import verificar_dirección_arch

dic_motores = {
    '.vpm': [ModeloVensim],
    '.mdl': [ModeloPySD, ModeloVensim],
    '.xml': [ModeloPySD],
    '.xmile': [ModeloPySD]

    # Agregar otros tipos de modelos DS aquí.
}


def generar_mds(archivo, motor=None, enforzar_instalado=True):
    """
    Esta función genera una instancia de modelo de DS. Identifica el tipo_mod de fuente por su extensión (p. ej., .vpm) y
    después genera una instancia de la subclase apropiada de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS`.

    Parameters
    ----------
    archivo : str
        El fuente del modelo DS.
    motor : type | list[type]
        Las clases de envoltura MDS que quieres considerar para generar este modelo.

    Returns
    -------
    EnvolturaMDS
        Un modelo DS.

    """

    archivo = verificar_dirección_arch(archivo)

    # Identificar la extensión.
    ext = os.path.splitext(archivo)[1]

    # Verificar si podemos leer este tipo_mod de fuente.
    if ext not in dic_motores:
        # Mensaje para modelos todavía no incluidos en Tinamit.
        raise ValueError(_('El tipo_mod de modelo "{}" no se acepta como modelo DS en Tinamit al momento. Si piensas'
                           'que podrías contribuir aquí, ¡contáctenos!').format(ext))
    else:
        errores = {}
        if motor is None:
            motores_potenciales = dic_motores[ext]
        else:
            if not isinstance(motor, list):
                motor = [motor]
            motores_potenciales = [x for x in dic_motores[ext] if x in motor]

        if not len(motores_potenciales):
            raise ValueError(_('No encontramos envoltura potencial para modelos de tipo "{}".').format(ext))

        for env in motores_potenciales:
            try:
                mod = env(archivo)  # type: EnvolturaMDS
                if mod.instalado() or not enforzar_instalado:
                    return mod
                else:
                    errores[env.__name__] = 'Programa no instalado.'
            except BaseException as e:
                errores[env.__name__] = e

        raise ValueError(_('El modelo "{}" no se pudo leer. Intentamos las envolturas siguientes, pero no funcionaron:'
                           '{}').format(archivo, ''.join(['\n\t{}: {}'.format(env, e) for env, e in errores.items()])))
