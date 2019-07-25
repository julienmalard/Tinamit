import os

from tinamit.config import _
from .pysd import ModeloPySD
from .vensim_dll import ModeloVensimDLL
from ._envolt import ModeloDS

_subclases = [ModeloPySD, ModeloVensimDLL]


def registrar_envolt_mds(envoltura):
    """
    Registra una nueva envoltura en Tinamït.

    Parameters
    ----------
    envoltura:
        La nueva envoltura.

    """
    _subclases.insert(0, envoltura)


def olvidar_envolt_mds(envoltura):
    """
    Borra una envoltura del registro global.

    Parameters
    ----------
    envoltura:
        La envoltura que ya no quieres.

    """
    _subclases.remove(envoltura)


class ErrorNoInstalado(OSError):
    """
    Error para devolver si no está instalada una envoltura.
    """
    pass


def gen_mds(archivo):
    """
    Automáticamente generar un :class:`~tinamit.envolt.mds._envolt.ModeloDS` desde un archivo.

    Parameters
    ----------
    archivo: str

    Returns
    -------
    ModeloDS

    """
    ext = os.path.splitext(archivo)[1]

    instaladas = [s for s in _subclases if s.instalado()]
    for cls in instaladas:
        ext_cls = [cls.ext] if isinstance(cls.ext, str) else cls.ext
        for e in ext_cls:
            e = '.' + e if ext[0] != '.' else e
            if ext == e:
                return cls(archivo)
    raise ErrorNoInstalado(_('No se encontró envoltura instalada para archivos de tipo "{}".'.format(ext)))
