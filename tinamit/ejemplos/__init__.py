from pkg_resources import resource_string


def obt_ejemplo(arch):
    return resource_string('tinamit.ejemplos', arch)
