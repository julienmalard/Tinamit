import os

from pkg_resources import resource_filename


def obt_ejemplo(arch):
    dirección = resource_filename(__name__, arch)
    if os.path.isfile(dirección):
        return dirección
    raise FileNotFoundError(dirección)
