from pkg_resources import resource_filename
from . import config
from .Modelo import Modelo
from .Conectado import Conectado
from . import EnvolturasMDS
from . import EnvolturasBF

# Cosas básicas
__author__ = 'Julien Malard'

__notes__ = 'Contacto: julien.malard@mail.mcgill.ca'

with open(resource_filename('tinamit', 'versión.txt')) as _archivo_versión:
    __versión__ = _archivo_versión.read().strip()

__version__ = __versión__

__all__ = ['config', 'Modelo', 'Conectado', 'EnvolturasBF', 'EnvolturasMDS']
