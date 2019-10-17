from mesa import Model
from tinamit.config import _

from ...utils import _importar_de_arch_python


def _gen_modelo(mod):
    if isinstance(mod, Model):
        raise TypeError('`mod` debe ser una clase de `mesa.Model`, y no una instancia.')
    elif callable(mod) and issubclass(mod, Model):
        return mod
    elif isinstance(mod, str):
        return _importar_de_arch_python(mod, clase=Model, nombre='Modelo', instanciar=False)
    raise ValueError(
        _('`modelo` debe ser un modelo mesa.Model, o un archivo '
          'Python que contiene uno, no {tipo}.').format(tipo=type(mod))
    )
