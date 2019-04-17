import os

from tinamit.config import _
from .pysd import EnvolturaPySDXMILE, EnvolturaPySDPy, EnvolturaPySDMDL
from .vensim_dll import EnvolturaVensimDLL

_subclases = [EnvolturaPySDXMILE, EnvolturaPySDPy, EnvolturaPySDMDL, EnvolturaVensimDLL]


def registrar_envolt_mds(envoltura):
    _subclases.insert(0, envoltura)


def olvidar_envolt_mds(envoltura):
    _subclases.remove(envoltura)


class ErrorNoInstalado(OSError):
    pass


def gen_mds(archivo):
    ext = os.path.splitext(archivo)[1]

    instaladas = [s for s in _subclases if s.instalado()]
    for cls in instaladas:
        ext_cls = [cls.ext] if isinstance(cls.ext, str) else cls.ext
        for e in ext_cls:
            e = '.' + e if ext[0] != '.' else e
            if ext == e:
                return cls(archivo)
    raise ErrorNoInstalado(_('No se encontró envoltura instalada para archivos de tipo "{}".'.format(ext)))
