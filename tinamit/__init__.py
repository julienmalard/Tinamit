from pkg_resources import resource_filename

from .config import conf, conf_mods, trads

# Cosas básicas
__autor__ = 'Julien Malard'

__correo__ = 'Contacto: julien.malard@mail.mcgill.ca'

with open(resource_filename('tinamit', 'versión.txt')) as _archivo_versión:
    __versión__ = _archivo_versión.read().strip()

__version__ = __versión__
