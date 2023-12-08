import gettext
import json
import os
from warnings import warn as avisar

from pkg_resources import resource_filename

from tinamit.cositas import cargar_json, guardar_json


# Código para manejar configuraciones de Tinamït
class OpsConfig(object):
    def __init__(símismo, pariente, valores=None):
        valores = valores or {}
        símismo.valores = {ll: OpsConfig(símismo, v) if isinstance(v, dict) else v for ll, v in valores.items()}
        símismo.pariente = pariente

    def a_dic(símismo):
        return {ll: v.a_dic() if isinstance(v, OpsConfig) else v for ll, v in símismo.valores.items()}

    def borrar(símismo, llave):
        if isinstance(llave, str):
            símismo.valores.pop(llave)
        elif len(llave) == 1:
            símismo.valores.pop(llave[0])
        else:
            símismo.valores[llave[0]].borrar(llave[1:])

    def guardar(símismo):
        símismo.pariente.guardar()

    def __contains__(símismo, itema):
        return itema in símismo.valores

    def __getitem__(símismo, itema):
        if isinstance(itema, str):
            return símismo.valores[itema]
        elif len(itema) == 1:
            return símismo.valores[itema[0]]
        else:
            return símismo.valores[itema[0]][itema[1:]]

    def __setitem__(símismo, llave, valor):
        if isinstance(llave, str):
            símismo.valores[llave] = valor
        elif len(llave) == 1:
            símismo.valores[llave[0]] = valor
        else:
            if not llave[0] in símismo:
                símismo.valores[llave[0]] = OpsConfig(pariente=símismo)
            símismo.valores[llave[0]][llave[1:]] = valor
        símismo.guardar()


class Config(OpsConfig):

    def __init__(símismo, archivo, auto=None):
        auto = auto or {}

        símismo.archivo = archivo
        símismo.val_auto = auto.copy()

        try:
            val_arch = cargar_json(archivo)
        except (FileNotFoundError, json.decoder.JSONDecodeError, PermissionError):
            val_arch = {}

        auto.update(val_arch)

        super().__init__(pariente=None,valores=auto)
        try:
            símismo.guardar()
        except OSError:
            pass

    def reinic(símismo):
        símismo.valores = OpsConfig(pariente=símismo, valores=símismo.val_auto)
        símismo.guardar()

    def borrar(símismo, llave):
        super().borrar(llave)
        símismo.guardar()

    def guardar(símismo):
        try:
            guardar_json(símismo.a_dic(), símismo.archivo)
        except PermissionError:
            avisar(_('No se pudo guardar la configuración.'))

    def __setitem__(símismo, llave, valor):
        super().__setitem__(llave, valor)
        símismo.guardar()


class Trads(object):
    AUX = 'aux'
    PRINC = 'principal'
    DOMINIO = 'leng'

    def __init__(símismo, dir_local):
        símismo.dir_local = dir_local
        símismo._conf = conf[Trads.DOMINIO]

        símismo._trads = símismo._regen_trads()

    def idioma(símismo):
        return símismo._conf[Trads.PRINC]

    def auxiliares(símismo):
        return símismo._conf[Trads.AUX]

    def cambiar_idioma(símismo, idioma):
        símismo._conf[Trads.PRINC] = idioma
        if idioma in símismo.auxiliares():
            símismo.auxiliares().pop(idioma)  # aprovechamos del enlace dinámico

        símismo._trads = símismo._regen_trads()

    def cambiar_aux(símismo, aux):
        if isinstance(aux, str):
            aux = [aux]

        principal = símismo.idioma()
        aux = [i for i in aux if i != principal]
        símismo._conf[Trads.AUX] = aux

        símismo._trads = símismo._regen_trads()

    def trad(símismo, texto):
        return símismo._trads.gettext(texto)

    def _regen_trads(símismo):
        return gettext.translation(
            __name__, localedir=símismo.dir_local, fallback=True,
            languages=[símismo.idioma()] + símismo.auxiliares()
        )


conf = Config(
    resource_filename('tinamit', 'config.json'),
    auto={
        Trads.DOMINIO: {Trads.PRINC: 'cak', Trads.AUX: ['es']},
        'envolt': {}
    }
)

conf_mods = conf['envolt']

trads = Trads(
    dir_local=os.path.join(os.path.abspath(os.path.dirname(__file__)), '_local', '_fuente')
)

_ = trads.trad
