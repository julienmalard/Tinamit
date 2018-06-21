import gettext
import json
import os
from warnings import warn as avisar

from chardet import UniversalDetector
from pkg_resources import resource_filename

# Cosas básicas
__author__ = 'Julien Malard'

__notes__ = 'Contacto: julien.malard@mail.mcgill.ca'

with open(resource_filename('tinamit', 'versión.txt')) as archivo_versión:
    __versión__ = archivo_versión.read().strip()

__version__ = __versión__


# Código para manejar configuraciones de Tinamït
def _escribir_json(dic, doc):
    if not os.path.isdir(os.path.split(doc)[0]):
        os.makedirs(os.path.split(doc)[0])

    with open(doc, 'w', encoding='utf8') as d:
        json.dump(dic, d, ensure_ascii=False, sort_keys=False, indent=2)


def _leer_json(doc):
    with open(doc, encoding='utf8') as d:
        return json.load(d)


_dir_config = resource_filename('tinamit', 'config.json')
_config_base = {
    'leng': 'es'
}
try:
    _configs = _leer_json(_dir_config)
    for c, v_c in _config_base.items():
        if c not in _configs:
            _configs[c] = v_c
except (FileNotFoundError, json.decoder.JSONDecodeError):
    _configs = _config_base.copy()
    _escribir_json(_configs, _dir_config)


def obt_val_config(llave, tipo=None, mnsj_err=None, suprm_err=False):
    """

    :param llave:
    :type llave: str
    :param mnsj_err:
    :type mnsj_err: str
    :return:
    :rtype: str | float | int
    """

    def verificar(v, tp):
        if tp is None:
            return True
        if tp.lower() == 'arch':
            return os.path.isfile(v)
        elif tp.lower() == 'dir':
            return os.path.isdir(v)
        else:
            raise ValueError

    try:
        val = _configs[llave]
        if not verificar(val, tipo):
            if suprm_err:
                avisar(mnsj_err)
                return
            else:
                raise FileNotFoundError(_('El archivo "" no existe.').format(val))
    except KeyError:
        if suprm_err:
            avisar(mnsj_err)
            return
        else:
            raise KeyError(_('Tinamït no tiene variable "{}" de configuración.').format(llave))

    return val


def poner_val_config(llave, val):
    _configs[llave] = val
    _escribir_json(_configs, _dir_config)


def poner_val_config_arch(llave, val):
    if not os.path.isfile(val):
        raise FileNotFoundError(_('El archivo "{}" no existe. :(').format(val))
    poner_val_config(llave=llave, val=val)


# Funciones fáciles para opciones de lenguas.
_dir_local = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'local', '_fuente')

lenguas = _configs['leng'] if isinstance(_configs['leng'], list) else [_configs['leng']]

_dic_trads = {'leng': lenguas[0],
              'otras': lenguas,
              'trads': gettext.translation(__name__, _dir_local, fallback=True, languages=lenguas)}


def cambiar_lengua(leng, temp=False):
    """
    Cambia la lengua de Tinamït.

    :param leng:
    :type leng: str | list[str]

    :param temp: Si el cambio es temporario (esta sesión) o el nuevo normal.
    :type temp: bool

    """

    if isinstance(leng, str):
        if leng in lenguas:
            lenguas.remove(leng)
        lenguas.insert(0, leng)

    elif isinstance(leng, list):
        lenguas.clear()
        lenguas.extend(leng)

    else:
        raise TypeError

    if not temp:
        poner_val_config('leng', leng)

    actualizar = False
    if _dic_trads['leng'] != lenguas[0]:
        actualizar = True
        _dic_trads['leng'] = lenguas[0]
    elif _dic_trads['otras'] != lenguas:
        actualizar = True
        _dic_trads['otras'] = lenguas
    if actualizar:
        _dic_trads['trads'] = gettext.translation(__name__, _dir_local, fallback=True, languages=lenguas)


def _(tx):
    """

    Parameters
    ----------
    tx :

    Returns
    -------
    str
    """
    return _dic_trads['trads'].gettext(tx)


def valid_nombre_arch(nombre):
    """
    Una función para validar un nombre de archivo.

    :param nombre: El nombre propuesto para el archivo.
    :type nombre: str
    :return: Un nombre válido.
    :rtype: str
    """
    for x in ['\\', '/', '\|', ':' '*', '?', '"', '>', '<']:
        nombre = nombre.replace(x, '_')

    return nombre.strip()


def detectar_codif(archivo, máx_líneas=None):
    detector = UniversalDetector()
    for í, línea in enumerate(open(archivo, 'rb').readlines()):
        detector.feed(línea)
        if máx_líneas is not None and í == (máx_líneas - 1):
            break
        if detector.done: break
    detector.close()
    return detector.result['encoding']
