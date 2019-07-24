from pkg_resources import resource_filename


def obt_ejemplo(arch):
    return resource_filename(__name__, arch)
