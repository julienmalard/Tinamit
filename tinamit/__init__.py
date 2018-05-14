import gettext
import json
import os

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


def obt_val_config(llave, tipo='arch', pedir=True, mnsj=None):
    """

    :param llave:
    :type llave: str
    :param tipo:
    :type tipo: str
    :param pedir:
    :type pedir: bool
    :param mnsj:
    :type mnsj: str
    :return:
    :rtype: str | float | int
    """

    def verificar(v, tp):
        if tp.lower() == 'arch':
            if not os.path.isfile(v):
                return False
        elif tp.lower() == 'dir':
            if not os.path.isdir(v):
                return False
        else:
            return True
        return True

    if pedir:

        try:
            val = _configs[llave]
        except KeyError:
            val = input(_('Entregar el valor para {}').format(llave) if mnsj is None else mnsj)

        while not verificar(val, tipo):
            val = input(_('"{}" no es un valor aceptable para "{}".\n\tIntente de nuevo:').format(val, llave))

        poner_val_config(llave, val)

    else:
        try:
            val = _configs[llave]
            if not verificar(val, tipo):
                raise FileNotFoundError(_('El archivo "" no existe.').format(val))
        except KeyError:
            raise KeyError(_('Tinamït no tiene variable "{}" de configuración.').format(llave))

    return val


def poner_val_config(llave, val):
    _configs[llave] = val
    _escribir_json(_configs, _dir_config)


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
