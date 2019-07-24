from pkg_resources import resource_filename

from .config import conf, conf_mods, trads

# Cosas básicas
__autor__ = 'Julien Malard'

__correo__ = 'Contacto: julien.malard@mail.mcgill.ca'

with open(resource_filename('tinamit', 'versión.txt')) as _archivo_versión:
    import os


    def list_files():
        print(1)
        dir_ = os.path.split(__file__)[0]
        print(dir_)
        for root, dirs, files in os.walk(dir_):
            level = root.replace(dir_, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print('{}{}'.format(subindent, f))
    list_files()

    __versión__ = _archivo_versión.read().strip()

__version__ = __versión__
