import pint
import regex as re

from tinamit.config import _
from tinamit.unids import regu, C_, trad_unid
from tinamit.unids.trads import buscar_singular


def convertir(de, a, val=1, lengua=None):
    """
    Esta función convierte un valor de una unidad a otra.

    Parameters
    ----------
    de : str
        La unidad original.
    a : str
        La unidad final.
    val : float | int
        El valor para convertir.
    lengua : str
        La lengua en la cual las unidades están especificadas.

    Returns
    -------
    float
        El valor convertido.
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

    # Reformatear exponentes para que los entienda Pint
    de = re.sub(r'([\p{l}\p{m}]+\w*)(-?[\p{n}]+)', repl=r'\1 ^ \2', string=de)
    a = re.sub(r'([\p{l}\p{m}]+\w*)(-?[\p{n}]+)', repl=r'\1 ^ \2', string=a)

    # Leer los nombres de todas las unidades presentes.
    unids_pres_de = re.findall(r'[\p{l}\p{m}]+', de)
    unids_pres_a = re.findall(r'[\p{l}\p{m}]+', a)
    unids_pres = list(set(unids_pres_de + unids_pres_a))

    # Agregar unidades no reconocidas por Pint
    for u in unids_pres:
        # Para cada tipo_mod de unidad detectada en las unidades iniciales...

        try:
            # Ver si Pint lo reconoce
            regu.parse_units(u)

        except pint.UndefinedUnitError:
            # Si Pint no lo reconoce...

            try:
                # Primero intentamos traducirlo para Pint
                u_t = trad_unid(u, leng_final='en', leng_orig=lengua)

                if u_t != u:
                    # Si la traducción se efectuó...

                    # ...reemplazar las unidades iniciales con la versión traducida.
                    regu.parse_units(u_t)  # Verificar que la traducción sí funcione.
                    if u in unids_pres_de:
                        de = re.sub(r'%s(?![\p{l}\p{m}])' % u, repl=u_t, string=de)
                    if u in unids_pres_a:
                        a = re.sub(r'%s(?![\p{l}\p{m}])' % u, repl=u_t, string=a)

                else:
                    # Si no encontramos traducción, registramos la nueva unidad con Pint.
                    definir_en_regu(unid=u, base=buscar_singular(u)[-1])

            except pint.UndefinedUnitError:
                # Si Pint no reconoció aún la traducción, tenemos que registrar la unidad.
                definir_en_regu(unid=u, base=buscar_singular(u)[-1])

    # Intentar convertir
    try:
        cant = C_(val, de).to(a)
        cant_convtd = cant.magnitude  # Guardar el valor convertido

    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError):
        # Si hasta ahora tenemos error, no puedo hacer nada más.
        raise ValueError(_('No se pudo convertir "{}" a "{}".').format(de_orig, a_orig))

    # Devolver la cantidad convertida
    return cant_convtd


def nueva_unidad(unid, ref, conv):
    regu.define('{unid} = {ref} * {conv}'.format(unid=unid, ref=ref, conv=conv))


def definir_en_regu(unid, base):
    """
    Esta funcion define una nueva unidad en el registro de unidades.

    Parameters
    ----------
    unid : str
        La unidad.
    base : str
        La dimensionalidad de la unidad para pasar a Pint.

    """

    # Detectar si la dimensionalidad ya se registró en Pint o no.
    try:
        base = regu.get_base_units(base)
        nueva_base = False
    except pint.errors.UndefinedUnitError:
        nueva_base = True

    if nueva_base:
        # Registrar la dimensionalidad, si necesario.
        regu.define('{b} = [{b}]'.format(b=base))
    if base != unid or not nueva_base:
        # Agregar la unidad a Pint si ya no se agregó con la dimensionalidad.
        regu.define('{u} = {b}'.format(u=unid, b=base))
