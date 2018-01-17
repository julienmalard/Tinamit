import json
import re

import pkg_resources

from tinamit import _

# Buscar el archivo de conversiones.
archivo_json = pkg_resources.resource_filename('tinamit.Unidades', 'equiv_unid.json')

# Leer las conversiones.
with open(archivo_json, 'r', encoding='utf8') as d:
    dic_doc = json.load(d)
    dic_conv = dic_doc['conv']
    dic_equiv = dic_doc['equiv']


def convertir(de, a, val=1, clase=None, lengua=None):
    """
    Esta función convierte un valor de una unidad a otra.

    :param de: La unidad original.
    :type de: str

    :param a: La unidad final.
    :type a: str

    :param clase: El tipo de unidad ('tiempo', 'distancia', etc.) No es obligatoria.
    :type clase: str

    :param val: El valor para convertir.
    :type val: float

    :param lengua: La lengua en la cuál se están especificando las unidades.
    :type lengua: str

    :return: El valor convertido.
    :rtype: float

    """

    # Estar seguro que diferencias en mayúsculos o espacios no causen problemas
    de = de.lower().replace(' ', '')
    a = a.lower().replace(' ', '')

    # Si son las mismas unidades, no hay nada que hacer, por supuesto.
    if de == a:
        return val

    # Asegurarse que la clase de unidades sea una lista.
    if clase is None:
        # Si no se especificó nada, buscar en todas las clases.
        clases = list(dic_conv)
    elif type(clase) is list:
        clases = clase
    else:
        clases = [clase]

    if lengua is None:
        lenguas = list(dic_equiv)
    elif type(lengua) is list:
        lenguas = lengua
    else:
        lenguas = [lengua]

    #
    re_unid = r'(?P<unid>[^\W\d]+)(?P<exp>\-?(?=\d)?[\d]*)'
    regex = r'(?P<oper>[\*\/]?){}+'.format(re_unid)
    unidades_de = list(re.finditer(regex, de))
    unidades_a = list(re.finditer(regex, a))
    if len(unidades_de) != len(unidades_a):
        raise ValueError(_('Unidades incompatibles: "{}" y "{}".').format(de, a))

    factor = 1
    for g_de, g_a in zip(unidades_de, unidades_a):
        u_de = g_de.group('unid')
        u_a = g_a.group('unid')
        e_de = g_de.group('exp') if g_de.group('exp') != '' else 1
        e_a = g_a.group('exp') if g_a.group('exp') != '' else 1
        o_de = g_de.group('oper')
        o_a = g_a.group('oper')
        if e_de != e_a or o_de != o_a:
            raise ValueError

        conv = convertir_unid_senc(de=u_de, a=u_a, clases=clases, lenguas=lenguas)
        if o_de == '/':
            e_de *= -1
        factor *= conv ** e_de

    return factor * val


def convertir_unid_senc(de, a, clases, lenguas):
    """
    Esta función convierte una unidad sencilla a otra.

    :param de: La unidad original.
    :type de: str

    :param a: La unidad final.
    :type a: str

    :param clases: El tipo de unidad ('tiempo', 'distancia', etc.)
    :type clases: list

    :param lenguas: La lengua en la cuál se están especificando las unidades.
    :type lenguas: list

    :return: El valor convertido.
    :rtype: float

    """

    for leng in lenguas:
        for c in clases:
            try:
                for unid, equivs in dic_equiv[leng][c].items():
                    if de in equivs:
                        de = unid
                    if a in equivs:
                        a = unid
            except KeyError:
                pass

    factor = None

    for c in clases:
        try:
            dic = dic_conv[c]
        except KeyError:
            raise KeyError('Clase de unidades "{}" no reconocida. Debe ser uno de:\n{}.'.format(
                clases,
                ', '.join(list(dic_conv))
            ))

        if de in dic:
            if a in dic[de]:
                factor = dic[de][a]
        if factor is None:
            if a in dic:
                if de in dic[a]:
                    factor = 1/dic[a][de]

        if factor is None:
            # Verificar si las dos unidades tendría conexión a una misma tercera unidad (por ejemplo,
            # cm y mm están vinculados a m, y por su relacion a m se podría establecer la relación entre ambos.)
            for unid in dic:
                if a in dic[unid] and de in dic[unid]:
                    factor = dic[unid][a] / dic[unid][de]
                    break

        if factor is not None:
            break

    if factor is None:
        raise ValueError('Las unidades de tiempo de los dos modelos ({} y {}) son incompatibles. Si'
                         'te parece irrazonable, puedes quejarte a nosotros.'.format(de, a))

    return factor
