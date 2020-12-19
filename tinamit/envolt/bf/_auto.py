from tinamit.config import _

from ._envolt import ModeloBF
from ..utils import _importar_de_arch_python


def gen_bf(mod):
    """
    Genera un modelo BF desde un archivo o una subclase de ModeloBF.

    Parameters
    ----------
    mod: str or type or ModeloBF

    Returns
    -------
    ModeloBF
        Una instancia del modelo BF.
    """

    if isinstance(mod, ModeloBF):
        return mod
    elif callable(mod):
        if issubclass(mod, ModeloBF):
            return mod()
    elif isinstance(mod, str):
        return _importar_de_arch_python(mod, clase=ModeloBF, nombre='Envoltura')
    raise TypeError(
        _('Debes dar o una instancia o subclase de `ModeloDS`, o la dirección de un archivo que contiene una.')
    )
