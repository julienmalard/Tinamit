import itertools
import json
import os

import pint
import pkg_resources
from shutil import copyfile as copiar_archivo

from tinamit import _
from . import regu


archivo_json = pkg_resources.resource_filename('tinamit.Unidades', 'trads_unids.json')
archivo_json_respaldo = pkg_resources.resource_filename('tinamit.Unidades', 'trads_unids_respl.json')

if not os.path.isfile(archivo_json):
    l_dic_trads = []
else:
    if os.path.isfile(archivo_json_respaldo):
        with open(archivo_json_respaldo, encoding='UTF-8') as d_j:
            l_dic_trads = json.load(d_j)  # type: list[dict]
        copiar_archivo(archivo_json_respaldo, archivo_json)
    else:
        try:
            with open(archivo_json, encoding='UTF-8') as d_j:
                l_dic_trads = json.load(d_j)  # type: list[dict]
        except json.JSONDecodeError:
            l_dic_trads = []


def _act_arch_trads(l_d_t):
    c_unids = set()

    for d in dir(regu.sys):
        c_unids.update(dir(getattr(regu.sys, d)))

    unids_doc = {d['en'][0].lower() for d in l_d_t if 'en' in d}
    unids_faltan = c_unids.difference(unids_doc)  # Unidades en Pint pero no en nuestro diccionario

    lengs = set(itertools.chain.from_iterable([list(d) for d in l_d_t]))
    for u in unids_faltan:
        d_u = {'en': [u]}
        d_u.update({l: [''] for l in lengs if l != 'en'})

        l_d_t.append(d_u)

    # Limpiar
    for d in l_d_t:
        for l, t in d.items():
            d[l] = list(set(t))
    l_d_t[:] = [d for d in l_d_t if all(len(t) and all(len(i) for i in t) for l, t in d.items())]

    copiar_archivo(archivo_json, archivo_json_respaldo)

    try:
        with open(archivo_json, 'w', encoding='UTF-8') as d:
            json.dump(l_d_t, d, ensure_ascii=False, indent=2)
    except PermissionError:
        pass

    try:
        os.remove(archivo_json_respaldo)
    except (PermissionError, FileNotFoundError):
        pass


_act_arch_trads(l_d_t=l_dic_trads)


def trad_unid(unid, leng_final, leng_orig=None):
    unid = unid.lower()

    if unid[-1] == 's':
        l_u = [unid, unid[:-1]]
    else:
        l_u = [unid]

    unid_t = None
    if leng_orig is None:

        for u in l_u:
            unid_t = next((x[leng_final] for x in l_dic_trads if
                           (u in itertools.chain.from_iterable(x.values()) and leng_final in x)
                           ), None)
            if unid_t is not None:
                break
    else:
        for u in l_u:
            unid_t = next((x[leng_final] for x in l_dic_trads if
                           (leng_orig in x and u in x[leng_orig] and leng_final in x)
                           ), None)
            if unid_t is not None:
                break

    if unid_t is None and (leng_orig == 'en' or leng_orig is None):
        try:
            unid_base = regu.get_root_units(unid)[1]

            unid_t = next((x[leng_final] for x in l_dic_trads if
                           ('en' in x and unid_base in x['en'] and leng_final in x)
                           ), None)
        except pint.UndefinedUnitError:
            pass

    if unid_t is None or not len(unid_t):
        unid_t = unid
    else:
        unid_t = unid_t[0]

    return unid_t


def agregar_trad(unid, trad, leng_trad, leng_orig=None, guardar=True):
    d_unid = _buscar_d_unid(unid=unid, leng=leng_orig)

    if leng_trad not in d_unid:
        d_unid[leng_trad] = []

    if isinstance(trad, str):
        if trad not in d_unid[leng_trad]:
            d_unid[leng_trad].append(trad)
    elif isinstance(trad, list):
        if trad[0] not in d_unid[leng_trad]:
            d_unid[leng_trad] = trad
        else:
            d_unid[leng_trad][trad[0]] += trad[1:]

    else:
        raise TypeError()

    if guardar:
        _act_arch_trads(l_dic_trads)


def agregar_sinónimos(unid, sinónimos, leng=None, guardar=True):
    d_unid = _buscar_d_unid(unid=unid, leng=leng)
    if isinstance(sinónimos, str):
        d_unid[leng].append(sinónimos)
    elif isinstance(sinónimos, list):
        d_unid[leng] += sinónimos
    else:
        raise TypeError()

    if guardar:
        _act_arch_trads(l_dic_trads)


def _buscar_d_unid(unid, leng=None):
    unid = unid.lower()
    if leng is None:
        d_unid = next((x for x in l_dic_trads if any(unid in y for y in x.values())), None)
        if d_unid is None:
            if unid[-1] == 's':
                d_unid = next((x for x in l_dic_trads if any(unid[:-1] in y for y in x.values())), None)
        if d_unid is None:
            raise ValueError(_('La unidad "{}" no existe en cualquier lengua conocida.').format(unid))
    else:
        d_unid = next((x for x in l_dic_trads if leng in x and unid in x[leng]), None)
        if d_unid is None:
            pluriales = ['s', 'es', 'ें', 'கள்', 'க்கள்']
            for p in pluriales:
                t = len(p)
                if unid[-t] == p:
                    d_unid = next((x for x in l_dic_trads if leng in x and unid[:-t] in x[leng]), None)

        if d_unid is None:
            raise ValueError(_('La unidad "{}" no existe en la lengua "{}".').format(unid, leng))

    return d_unid
