import inspect
import os
import sys
import traceback
from importlib import import_module
from warnings import warn as avisar

from tinamit.config import _


def _importar_de_arch_python(archivo, clase, nombre, instanciar=True):
    if not os.path.isfile(archivo):
        raise FileNotFoundError(_('El archivo siguiente no existe... :(\n\t{}').format(archivo))

    if os.path.splitext(archivo)[1] != '.py':
        raise ValueError(_('El archivo siguiente no parece ser un archivo Python.').format(archivo))

    dir_mod, nombre_mod = os.path.split(archivo)
    sys.path.append(dir_mod)
    módulo = import_module(os.path.splitext(nombre_mod)[0])
    clases = {
        nmb: cls for nmb, cls in inspect.getmembers(
            módulo, lambda x: (inspect.isclass(x) and issubclass(x, clase))
        )
    }
    if instanciar:
        instancias = {nmb: cls for nmb, cls in inspect.getmembers(módulo, lambda x: isinstance(x, clase))}
        if 'Envoltura' in instancias:
            return instancias['Envoltura']
        elif instancias:
            return list(instancias.values())[0]

    potenciales = {}
    errores = {}
    for nmb, cls in clases.items():
        # noinspection PyBroadException
        try:
            potenciales[nmb] = cls() if instanciar else cls
        except NotImplementedError:
            continue
        except Exception:
            errores[nmb] = traceback.format_exc()
            continue

    if len(potenciales) == 1:
        return list(potenciales.values())[0]
    elif 'Envoltura' in potenciales:
        return potenciales['Envoltura']
    elif potenciales:
        nmb_elegida = list(potenciales)[0]
        avisar(_('\nHabía más de una instancia o subclase de `{clase}` en el fuente'
                 '\n\t{arch}'
                 '\n...y ninguna se llamaba "{nombre}". Tomaremos "{elegida}" como la envoltura'
                 '\ny esperaremos que funcione. Si no te parece, asegúrate que la definición de clase o el'
                 '\nobjeto correcto se llame "{nombre}".'
                 ).format(clase=clase, nombre=nombre, arch=archivo, elegida=nmb_elegida))
        return potenciales[nmb_elegida]

    raise AttributeError(_(
        'El archivo especificado: \n\t{arch}\nno contiene subclase o instancia de `{clase}` utilizable. '
        '\nErrores encontrados:{err}'
    ).format(
        arch=archivo, clase=clase,
        err=''.join(['\n\n\t{}: \n{}'.format(nmb, e) for nmb, e in errores.items()]))
    )
