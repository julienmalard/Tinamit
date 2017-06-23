from pkg_resources import resource_filename
from . import Incertidumbre, Interfaz

__author__ = 'Julien Malard'

__notes__ = 'Contacto: julien.malard@mail.mcgill.ca'


with open(resource_filename('tinamit', 'versión.txt')) as archivo_versión:
    versión = archivo_versión.read().strip()

__version__ = versión


def correr():
    Interfaz.correr()