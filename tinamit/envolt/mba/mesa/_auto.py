from tinamit.config import _
from ._envolt import EnvoltModeloMesa
from ...utils import _importar_de_arch_python


def _gen_modelo(mod):
    if isinstance(mod, EnvoltModeloMesa):
        raise TypeError('`mod` debe ser una clase de `mesa.Model`, y no una instancia.')
    elif callable(mod) and issubclass(mod, EnvoltModeloMesa):
        return mod
    elif isinstance(mod, str):
        return _importar_de_arch_python(mod, clase=EnvoltModeloMesa, nombre='Modelo', instanciar=False)
    raise ValueError(
        _('`modelo` debe ser una subclase de tinamit.envolt.mba.mesa.EnvoltModeloMesa, o un archivo '
          'Python que contiene una, no "{mod}".').format(mod=mod)
    )
