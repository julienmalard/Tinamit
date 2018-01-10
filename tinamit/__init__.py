from pkg_resources import resource_filename
import os
import json

__author__ = 'Julien Malard'

__notes__ = 'Contacto: julien.malard@mail.mcgill.ca'


with open(resource_filename('tinamit', 'versión.txt')) as archivo_versión:
    __versión__ = archivo_versión.read().strip()

__version__ = __versión__


def _escribir_json(dic, doc):
    if not os.path.isdir(os.path.split(doc)[0]):
        os.makedirs(os.path.split(doc)[0])

    with open(doc, 'w', encoding='utf8') as d:
        json.dump(dic, d, ensure_ascii=False, sort_keys=False, indent=2)


def _leer_json(doc):
    with open(doc, encoding='utf8') as d:
        return json.load(d)


_dir_config = resource_filename('tinamit', 'config.json')
try:
    _configs = _leer_json(_dir_config)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    _configs = {}
    _escribir_json(_configs, _dir_config)


def obt_val_config(llave, tipo='arch', pedir=True):

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
            val = input(llave)

        while not verificar(val, tipo):
            val = input(llave)

        poner_val_config(llave, val)

    else:
        try:
            val = _configs[llave]
            if not verificar(val, tipo):
                raise FileNotFoundError('')
        except KeyError:
            raise KeyError('')

    return val


def poner_val_config(llave, val):
    _configs[llave] = val
    _escribir_json(_configs, _dir_config)
