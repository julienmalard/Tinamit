import pint
import regex as re

from tinamit import _
from tinamit.Unidades import regu, C_, trad_unid


def convertir(de, a, val=1, lengua=None):
    """
    Esta función convierte un valor de una unidad a otra.

    :param de: La unidad original.
    :type de: str

    :param a: La unidad final.
    :type a: str

    :param val: El valor para convertir.
    :type val: float | int

    :param lengua: La lengua en la cual las unidades están especificadas.
    :type lengua: str

    :return: El valor convertido.
    :rtype: float

    """

    # Guardar una copia de los unidades iniciales
    de_orig = de
    a_orig = a

    # Estar seguro que diferencias en mayúsculos o espacios no causen problemas
    de = de.lower().strip()
    a = a.lower().strip()

    # Si son las mismas unidades, no hay nada que hacer, por supuesto.
    if de == a:
        return val

    # Leer los nombres de todas las unidades presentes.
    unids_pres_de = re.findall(r'[\p{l}\p{m}]+', de)
    unids_pres_a =  re.findall(r'[\p{l}\p{m}]+', a)
    unids_pres = list(set(unids_pres_de + unids_pres_a))

    # Agregar unidades no reconocidas por Pint
    for u in unids_pres:
        try:
            regu.parse_units(u)
        except pint.UndefinedUnitError:
            try:
                u_t = trad_unid(u, leng_final='en', leng_orig=lengua)
                if u_t != u:
                    regu.parse_units(u_t)
                    if u in unids_pres_de:
                        de = re.sub(r'%s(?![\p{l}\p{m}])' % u, repl=u_t, string=de)
                    if u in unids_pres_a:
                        a = re.sub(r'%s(?![\p{l}\p{m}])' % u, repl=u_t, string=a)
            except pint.UndefinedUnitError:
                regu.define('{u} = [{u}]'.format(u=u))

    try:
        cant = C_(val, de).to(a)
        cant_convtd = cant.magnitude
    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError):
        raise ValueError(_('No se pudo convertir "{}" a "{}".').format(de_orig, a_orig))

    return cant_convtd
