from pkg_resources import resource_filename


# Cosas básicas
__author__ = 'Julien Malard'

__notes__ = 'Contacto: julien.malard@mail.mcgill.ca'

with open(resource_filename('tinamit', 'versión.txt')) as _archivo_versión:
    __versión__ = _archivo_versión.read().strip()

__version__ = __versión__



