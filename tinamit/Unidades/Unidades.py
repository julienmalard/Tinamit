import json
import os

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'equiv_unid.json'), 'r', encoding='utf8') as d:
    dic_doc = json.load(d)
    dic_conv = dic_doc['conv']
    dic_equiv = dic_doc['equiv']


def convertir(de, a,  val=1, clase=None, lengua=None):
    """
    Esta función convirte un valor de una unidad a otra.

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

    de = de.lower()
    a = a.lower()

    if de == a:
        return val

    if clase is None:
        clase = list(dic_conv)
    elif type(clase) is str:
        clase = [clase]

    if lengua is None:
        lenguas = list(dic_equiv)
    elif type(lengua) is list:
        lenguas = lengua
    else:
        lenguas = [lengua]

    for leng in lenguas:
        for c in clase:
            try:
                for unid, equivs in dic_equiv[leng][c].items():
                    if de in equivs:
                        de = unid
                    if a in equivs:
                        a = unid
            except KeyError:
                pass

    factor = None

    for c in clase:
        try:
            dic = dic_conv[c]
        except KeyError:
            raise KeyError('Clase de unidades "{}" no reconocida. Debe ser uno de:\n{}.'.format(
                clase,
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

    return factor*val
