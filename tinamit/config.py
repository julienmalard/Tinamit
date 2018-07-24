import gettext
import json
import os
from warnings import warn as avisar

from pkg_resources import resource_filename

from tinamit.cositas import cargar_json, guardar_json

# Código para manejar configuraciones de Tinamït
_dir_config = resource_filename('tinamit', 'config.json')
_config_base = {
    'leng': 'es',
    'lengs_aux': [],
    'envolturas': {}
}


def _guardar_conf():
    guardar_json(_configs, _dir_config)


try:
    _configs = cargar_json(_dir_config)
    for c, v_c in _config_base.items():  # pragma: sin cobertura
        if c not in _configs:
            _configs[c] = v_c
        elif not isinstance(_configs[c], type(v_c)):
            _configs[c] = v_c
    _guardar_conf()
except (FileNotFoundError, json.decoder.JSONDecodeError):
    _configs = _config_base.copy()
    _guardar_conf()


def obt_val_config(llave, cond=None, mnsj_err=None, respaldo=None):
    if not isinstance(respaldo, list):
        respaldo = [respaldo]

    try:
        conf, ll = _resolver_conf_anidado(llave)
        val = conf[ll]

        if cond is None:
            return val
        else:
            if cond(val):
                return val
            else:
                for a in respaldo:
                    if a is not None and cond(a):
                        return a
                if mnsj_err is not None:
                    avisar(mnsj_err)
                return

    except KeyError:
        val = None
        if cond is None:
            val = respaldo[0]
        else:
            for a in respaldo:
                if a is not None and cond(a):
                    val = a
        if val is None and mnsj_err is not None:
            avisar(mnsj_err)
        return val


def poner_val_config(llave, val):
    conf, ll = _resolver_conf_anidado(llave, crear=True)
    conf[ll] = val
    _guardar_conf()


def borrar_var_config(llave):
    try:
        conf, ll = _resolver_conf_anidado(llave)
        conf.pop(ll)
    except KeyError:
        raise KeyError(_('La llave "{}" no existía en la configuración.').format(llave))
    _guardar_conf()


def limpiar_config():  # pragma: sin cobertura
    _configs.clear()
    _configs.update(_config_base)
    _guardar_conf()


def _resolver_conf_anidado(llave, crear=False):
    if not isinstance(llave, list):
        llave = [llave]
    conf = _configs
    for ll in llave[:-1]:
        if crear and ll not in conf or not isinstance(conf[ll], dict):
            conf[ll] = {}
        conf = conf[ll]

    return conf, llave[-1]


# Funciones fáciles para opciones de lenguas.
_dir_local = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'local', '_fuente')

lengua = obt_val_config('leng')
lengs_aux = obt_val_config('lengs_aux')

_dic_trads = {'leng': lengua,
              'otras': lengs_aux,
              'trads': gettext.translation(__name__, _dir_local, fallback=True, languages=[lengua] + lengs_aux)}


def cambiar_lengua(leng, auxiliares=None, temp=False):
    """

    Parameters
    ----------
    leng : str
        La lengua en la cual quieres recibir los mensajes de Tinamït.
    auxiliares : list[str] | str
        Otras lenguas para emplear, si tu lengua no está disponible.
    temp : bool
        Si el cambio es temporario (esta sesión) o el nuevo normal.

    """

    if auxiliares is not None and not isinstance(auxiliares, list):
        auxiliares = [auxiliares]

    if not temp:
        poner_val_config('leng', leng)
        if auxiliares is not None:
            poner_val_config('lengs_aux', auxiliares)
    if auxiliares is None:
        auxiliares = obt_val_config('lengs_aux')

    if _dic_trads['leng'] != leng or _dic_trads['otras'] != auxiliares:
        _dic_trads['trads'] = gettext.translation(__name__, _dir_local, fallback=True, languages=[leng] + auxiliares)


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
