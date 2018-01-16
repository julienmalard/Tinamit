import json
import os
import gettext

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
_dir_local = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'local')
dic_trads = {'es': gettext.translation(__name__, _dir_local, fallback=True, languages=['es'])}


def obt_trads():
    """
    Dewuelve un objeto de traducción.
    :return:
    :rtype:
    """

    leng = _configs['leng']
    return dic_trads[leng]


def cambiar_leng(leng):
    """
    Cambia la lengua de Tinamït.

    :param leng:
    :type leng: str

    """

    _configs['leng'] = leng
    if leng not in dic_trads:
        dic_trads[leng] = gettext.translation(__name__, _dir_local, fallback=True, languages=[leng])


def _(tx):
    return obt_trads().gettext(tx)