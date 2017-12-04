from pkg_resources import resource_filename


__author__ = 'Julien Malard'

__notes__ = 'Contacto: julien.malard@mail.mcgill.ca'


with open(resource_filename('tinamit', 'versión.txt')) as archivo_versión:
    versión = archivo_versión.read().strip()

__version__ = versión
