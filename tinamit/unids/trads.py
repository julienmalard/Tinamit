import json
import os
from itertools import chain as cadena

import babel
import pint
import pkg_resources
from pint import UnitRegistry
from tinamit.config import _
from tinamit.cositas import guardar_json, cargar_json

regu = UnitRegistry()
C_ = regu.Quantity

_archivo_trads = pkg_resources.resource_filename('tinamit.unids', 'trads_unids.json')
_archivo_pluriales = pkg_resources.resource_filename('tinamit.unids', 'pluriales.json')

l_dic_trads = None

if l_dic_trads is None:
    if os.path.isfile(_archivo_trads):
        try:
            l_dic_trads = cargar_json(_archivo_trads)
        except json.JSONDecodeError:  # pragma: sin cobertura
            l_dic_trads = []
    else:
        l_dic_trads = []

if os.path.isfile(_archivo_pluriales):
    _pluriales = cargar_json(_archivo_pluriales)
else:  # pragma: sin cobertura
    _pluriales = ['s', 'es', 'ें', 'கள்', 'க்கள்']
    guardar_json(_pluriales, _archivo_pluriales)


def act_arch_trads(l_d_t):
    """
    Actualiza el fuente de traducciones.

    Parameters
    ----------
    l_d_t : list[dict]

    """
    antes = hash(str(l_d_t))

    # UN conjunto vacío para las unidades presentes
    c_unids = set()

    # Agregar todas las unidades de Pint
    for d in dir(regu.sys):
        c_unids.update(u.lower() for u in dir(getattr(regu.sys, d)))

    # Todas las unidades ya en nuestro diccionario que podrían estar en Pint también.
    unids_doc = {d['en']['pr'].lower() for d in l_d_t if 'en' in d}

    # unids en Pint pero no en nuestro diccionario
    unids_faltan = c_unids.difference(unids_doc)

    # Lenguas ya incluidas en nuestro diccionario
    lengs = set(cadena.from_iterable([list(d) for d in l_d_t]))

    # Agregar las unidades de Pint que faltan
    for u in unids_faltan:  # pragma: sin cobertura
        d_u = {'en': {'pr': u, 'sn': []}}
        d_u.update({lng: {'pr': '', 'sn': []} for lng in lengs if lng != 'en'})
        l_d_t.append(d_u)

    # Limpiar el diccionario de traducciones
    for d in l_d_t:
        # Para cada unidad...
        for l, t in d.items():  # type: str, dict
            # Para cada lengua y diccionario de traducción...

            # Quitar nombres de unidades que estarían en la lista de sinónimos por error
            if t['pr'] in t['sn']:
                t['sn'].remove(t['pr'])

            d[l]['sn'] = list(set(t['sn']))  # Quitar sinónimos duplicados
            d[l]['sn'].sort()  # Ordenar los sinónimos

    # Guardar el diccionario de traducciones si hubieron modificaciones
    if hash(str(l_d_t)) != antes:
        try:
            guardar_json(obj=l_d_t, arch=_archivo_trads)
        except OSError:
            pass


def trad_unid(unid, leng_final, leng_orig=None, falla_silencio=True):
    """
    Traduce una unidad sencilla (no compuesta).

    Parameters
    ----------
    unid : str
        La unidad para traducir.
    leng_final : str
        La lengua a la cual traducir.
    leng_orig : str
        La lengua original de la unidad. Si no se especifica, se intentará adivinarla.
    falla_silencio: bool
        Si hay que devolver un error si no se encontró traducción.

    Returns
    -------
    str
        La unidad traducida.

    """

    # Quitar mayúsculas
    unid = unid.lower()

    l_u = buscar_singular(unid)

    # Buscar la unidad traducida
    unid_t = None
    if leng_orig is None:
        # Si no conocemos la lengua original, buscar todas.
        for u in l_u:
            unid_t = next((x[leng_final] for x in l_dic_trads
                           if (any([u == d['pr'] for d in x.values()]) or  # si `u` igual a la unidad principal
                               u in cadena.from_iterable([y['sn'] for y in x.values()])  # `u` igual a sinónimo
                               and leng_final in x  # ...y la lengua final existe
                               )
                           ), None)
            # Si encontramos la traducción, parar aquí.
            if unid_t is not None:
                break
    else:
        # Si conocemos la lengua original, solamente intentar las traducciones en esta lengua
        for u in l_u:
            unid_t = next(
                (x[leng_final] for x in l_dic_trads if  # El diccionario de la unidad traducida
                 (leng_orig in x  # Si la lengua original existe para esta unidad
                  and (u == x[leng_orig]['pr'] or u in x[leng_orig]['sn'])  # u igual a la unidad o sinónimos
                  and leng_final in x  # Y la lengua final también existe
                  )),
                None)

            # Si encontramos la traducción, parar aquí.
            if unid_t is not None:
                break

    # Si todavía no encontramos nada y la lengua original queda en inglés, ver si Pint nos pueda ayudar
    if unid_t is None and (leng_orig == 'en' or leng_orig is None):
        for u in l_u:
            try:
                u_base = regu.get_name(u)

                unid_t = next((x[leng_final] for x in l_dic_trads if
                               ('en' in x  # La traducción inglés existe
                                and (u_base in x['en']['sn'] or u_base == x['en']['pr'])  # La unidad corresponde
                                and leng_final in x)  # ...y la lengua final también existe
                               ), None)
            except pint.UndefinedUnitError:
                # Si no existía en Pint, seguir por el momento
                pass

    if unid_t is None or not len(unid_t):
        if falla_silencio:
            # Devolver la unidad no traducida si no encontramos nada
            unid_t = unid
        else:
            raise ValueError(_('No pudimos traducir "{u}" a la lengua "{leng}"').format(u=unid, leng=leng_final))
    else:
        # Devolver la traducción principal (no sinónimos) si encontramos algo
        unid_t = unid_t['pr']

    # Devolver la traducción
    return unid_t


def agregar_trad(unid, trad, leng_trad, leng_orig=None, guardar=True):
    """
    Agregar una traducción a una unidad.

    Parameters
    ----------
    unid : str
        La unidad original.
    trad : str
        La traducción de la unidad.
    leng_trad : str
        La lengua de la traducción.
    leng_orig : str
        La lengua original.
    guardar : bool
        Si hay que guardar la traducción para futuras sesiones de Python.

    """
    # Buscar el diccionario de la unidad
    d_unid = _buscar_d_unid(unid=unid, leng=leng_orig)

    # Si la lengua no existía, agragarla.
    if leng_trad not in d_unid:
        d_unid[leng_trad] = {'pr': '', 'sn': []}

    # Agregar la traducción
    if len(d_unid[leng_trad]['pr']):
        # Si ya existía traducción, agregar ésta como sinónima
        if trad not in d_unid[leng_trad]['sn']:
            d_unid[leng_trad]['sn'].append(trad)
    else:
        # Si no existía traducción, ésta será la versión principal de la unidad.
        d_unid[leng_trad]['pr'] = trad

    # Guardar si necesario.
    if guardar:
        act_arch_trads(l_dic_trads)


def agregar_sinónimos(unid, sinónimos, leng, guardar=False):
    """
    Agrega sinónimos a una unidad.

    Parameters
    ----------
    unid : str
        La unidad original.
    sinónimos : str | list
        Los sinónimos.
    leng : str
        La lengua.
    guardar : bool
        Si guardamos los sinónimos para futuras sesiones de Python.

    """
    # Buscar el diccionario de la unidad.
    d_unid = _buscar_d_unid(unid=unid, leng=leng)

    # Agregar los sinónimos
    if isinstance(sinónimos, str):
        sinónimos = [sinónimos]
    for s in sinónimos:
        if s not in d_unid[leng]['sn']:
            d_unid[leng]['sn'].append(s)

    # Guardar si necesario
    if guardar:
        act_arch_trads(l_dic_trads)


def _buscar_d_unid(unid, leng=None):
    """
    Busca el diccionario de una unidad.

    Parameters
    ----------
    unid : str
        El nombre de la unidad.
    leng : str
        La lengua de la unidad.

    Returns
    -------
    dict
        El diccionario de las traducciones de la unidad.

    """

    # Quitar mayúculas
    unid = unid.lower()

    l_u = buscar_singular(unid)
    d_unid = None

    for u in l_u:

        if leng is None:
            # Si no conocemos la lengua, buscar en todas las posibilidades.
            d_unid = next((x for x in l_dic_trads
                           if any(u in y['sn'] or u == y['pr'] for y in x.values())
                           ), None)
        else:
            # Si conocemos la lengua, buscar únicamente en las unidades de ésta.
            d_unid = next((x for x in l_dic_trads
                           if leng in x and (u in x[leng]['sn'] or u == x[leng]['pr'])
                           ), None)

        if d_unid is not None:
            # Si encontramos algo, para aquí.
            break

    # Si todavía no encontramos nada y la lengua original queda en inglés, ver si Pint nos pueda ayudar
    if d_unid is None and (leng == 'en' or leng is None):
        for u in l_u:
            try:
                u_base = regu.get_name(u)

                d_unid = next((x for x in l_dic_trads
                               if 'en' in x and (u_base in x['en']['sn'] or u_base == x['en']['pr'])
                               ), None)

            except pint.UndefinedUnitError:
                # Si no existía en Pint, seguir por el momento
                pass

    # Si todavía no encontramos nada, tenemos un error
    if d_unid is None:
        if leng is None:
            raise ValueError(_('La unidad "{}" no existe en cualquier lengua conocida.').format(unid))
        else:
            raise ValueError(_('La unidad "{u}" no existe en la lengua "{lng}".').format(u=unid, lng=leng))

    # Devolver el diccionario de unidad encontrado.
    return d_unid


def buscar_singular(u):
    """
    Busca las formas singulares posibles de una unidad.

    Parameters
    ----------
    u : str
        La unidad potencialmente plurial.

    Returns
    -------
    list[str]
        Una lista de las formas singulares potenciales.

    """

    # Generar una lista de la unidad y de potenciales formas singulares
    l_u = [u]
    for p in _pluriales:
        try:
            if u.endswith(p):
                l_u.append(u[:-len(p)])
        except IndexError:
            pass  # En el caso que la extensión plural sea más grande que la unidad sí misma.

    return l_u


# Actualizar las traducciones al importar este módulo
if os.path.getmtime(babel.__file__) > os.path.getmtime(_archivo_trads):
    act_arch_trads(l_d_t=l_dic_trads)
básicas = {
    'month': 'mes',
    'year': 'año',
    'day': 'día'
}
for ll, v in básicas.items():
    agregar_trad(ll, v, leng_trad='es', leng_orig='en')
