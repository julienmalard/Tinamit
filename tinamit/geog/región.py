import csv
import os
from collections import OrderedDict

from tinamit.config import _
from tinamit.cositas import detectar_codif


class Nivel(object):
    """
    Un nivel geográfico (p. ej, ``municipio`` o ``departamento``.
    """
    def __init__(símismo, nombre, subniveles=None):
        """

        Parameters
        ----------
        nombre: str
            El nombre del nivel.
        subniveles: list of Nivel
            Lista de subniveles.
        """
        símismo.nombre = nombre
        símismo.subniveles = subniveles

    def __eq__(símismo, otro):
        return str(símismo) == str(otro)

    def __str__(símismo):
        return símismo.nombre

    def __getitem__(símismo, itema):
        return next(n for n in símismo.subniveles if n == itema)

    def __hash__(símismo):
        return hash(str(símismo))


class Lugar(object):
    """
    Un lugar dado en una geografía.
    """
    def __init__(símismo, nombre, nivel, cód=None, sub_lugares=None):
        """

        Parameters
        ----------
        nombre: str
            El nombre del lugar.
        nivel: Nivel
            El nivel geográfico correspondiente.
        cód: str
            El identificador único de este lugar. Si es ``None``, se tomará su nombre como identificador.
        sub_lugares:
            Lugares que se encuentre adentro de este.
        """
        símismo.cód = cód or nombre
        símismo.nivel = nivel
        símismo.nombre = nombre
        símismo.sub_lugares = set(sub_lugares or [])

        símismo.ord_niveles = _OrdNiveles(símismo)

    def lugares(símismo, en=None, nivel=None):
        """
        Devolver los sublugares presentes en este lugar.

        Parameters
        ----------
        en: str or Lugar
            Sublugar al cual limitir la búsqueda.
        nivel: Nivel or str or list
            Opción para limitir los resultados a uno o más niveles.

        Returns
        -------
        set[Lugar]
        """
        if isinstance(nivel, (str, Nivel)):
            nivel = [nivel]
        if en is None:
            buscar_en = símismo
        else:
            buscar_en = símismo[en]
        return {lg for lg in buscar_en if (nivel is None or lg.nivel in nivel)}

    def buscar_nombre(símismo, nombre, nivel=None):
        """
        Devuelve el sublugar con el nombre dado.

        Parameters
        ----------
        nombre: str
            El nombre del lugar deseado.
        nivel: Nivel or str
            Desambiguación en el caso que hayan múltiples lugares con el mismo nombre en distintos niveles.

        Returns
        -------
        Lugar

        """
        for lg in símismo:
            if lg.nombre == nombre and (nivel is None or lg.nivel == nivel):
                return lg
        raise ValueError(_('Lugar "{nmb}" no encontrado en "{lg}"').format(nmb=nombre, lg=símismo))

    def pariente(símismo, lugar, ord_niveles=None, todos=False):
        """
        Obtener el pariente de un sublugar dado.

        Parameters
        ----------
        lugar: str or Lugar
            Un sublugar cuyo pariente queremos.
        ord_niveles: list
            Desambiguación para lugares con niveles paralelos.
        todos: bool
            Si queremos todos los parientes del lugar, o solamente el más cercaco.

        Returns
        -------
        Lugar

        """
        lugar = símismo[lugar]
        ord_niveles = símismo.ord_niveles.resolver(ord_niveles)
        potenciales = [lg for lg in símismo if lugar in lg.sub_lugares and lg.nivel in ord_niveles]
        if potenciales:
            if todos:
                return sorted(potenciales, key=lambda x: ord_niveles.index(str(x.nivel)))
            return sorted(potenciales, key=lambda x: ord_niveles.index(str(x.nivel)))[0]

    def hijos_inmediatos(símismo, ord_niveles=None):
        """
        Devuelve los hijos inmediatos de este ``Lugar``.

        Parameters
        ----------
        ord_niveles: list
            Desambiguación para lugares con niveles paralelos.

        Returns
        -------
        list[Lugar]

        """

        return [lg for lg in símismo if símismo.pariente(lg, ord_niveles=ord_niveles) == símismo]

    def __iter__(símismo):
        yield símismo
        for lg in símismo.sub_lugares:
            for s_lg in lg:
                yield s_lg

    def __getitem__(símismo, itema):
        for lg in símismo:
            if isinstance(itema, Lugar) and lg is itema:
                return lg
            elif itema == lg.cód:
                return lg

        raise KeyError(itema)

    def __str__(símismo):
        return símismo.nombre


class _OrdNiveles(object):
    def __init__(símismo, lugar):

        sub_ords = list(set(sub.ord_niveles.ords for sub in lugar.sub_lugares))
        ords = []
        for sb in sub_ords:
            for i, nv in enumerate(sb):
                if i > (len(ords) - 1):
                    ords.append(nv)
                else:
                    ant = ords[i]
                    if isinstance(ant, Nivel) and ant != nv:
                        ords[i] = (ant, nv)
                    elif isinstance(ant, tuple) and nv not in ant:
                        ords[i] = (*ant, nv)

        símismo.ords = (*ords, lugar.nivel)

    def resolver(símismo, orden=None):
        if orden is None:
            return [x if isinstance(x, Nivel) else x[0] for x in símismo.ords]

        if isinstance(orden, (str, Nivel)):
            orden = [orden]
        return orden

    def __contains__(símismo, itema):
        for x in símismo.ords:
            if (isinstance(x, Nivel) and x == itema) or (itema in x):
                return True
        return False


def gen_lugares(archivo, nivel_base, nombre=None, col_cód='Código'):
    """
    Genera un lugar con todos los niveles y sublugares asociados desde un archivo ``.csv``.

    Cada columna en el ``.csv`` debe empezar con el nombre de un nivel, con la excepción de la columna ``col_cód``,
    la cual tendrá el código identificador único de cada lugar.

    Cada fila representa un lugar, con su **nombre** en la columna correspondiendo al nivel de este lugar y
    el **código** del lugar pariente en las otras columnas. Si un nivel no se aplica a un lugar (por ejemplo,
    un departamento no tendrá municipio pariente), se deja vacía la célula.

    Parameters
    ----------
    archivo: str
        El archivo ``.csv``.
    nivel_base: str
        El el nivel más alto. Por ejemplo, si tu csv entero representa un país, sería ``país``.
    nombre: str
        El nombre del lugar correspondiendo al nivel más alto. Por ejemplo, "Guatemala".
    col_cód: str
        El nombre de la columna con los códigos de cada sublugar.

    Returns
    -------
    Lugar
    """
    codif_csv = detectar_codif(archivo)
    nombre = nombre or os.path.splitext(os.path.split(nombre)[1])[0]

    with open(archivo, newline='', encoding=codif_csv) as d:

        lc = csv.DictReader(d)  # El lector de csv

        # Guardar la primera fila como nombres de columnas
        cols = [x.strip() for x in lc.fieldnames]

        if col_cód not in cols:
            raise ValueError(_(
                'La columna de código de región especificada ("{c}") no concuerda con los nombres de '
                'columnas del csv ({n}).'
            ).format(c=col_cód, n=', '.join(cols)))

        doc = [OrderedDict((ll.strip(), v.strip()) for ll, v in f.items()) for f in lc]

    # Inferir el orden de la jerarquía
    órden = []

    escalas = [x for x in cols if x != col_cód]

    coescalas = []
    for f in doc:
        coescalas_f = {ll for ll, v in f.items() if len(v) and ll in escalas}
        if not any(x == coescalas_f for x in coescalas):
            coescalas.append(coescalas_f)

    coescalas.sort(key=lambda x: len(x))

    while len(coescalas):
        siguientes = {x.pop() for x in coescalas if len(x) == 1}
        if not len(siguientes):
            raise ValueError(_('Parece que hay un error con el fuente de información regional.'))
        órden.append(sorted(list(siguientes)) if len(siguientes) > 1 else siguientes.pop())
        for cn in coescalas.copy():
            cn.difference_update(siguientes)
            if not len(cn):
                coescalas.remove(cn)

    órden.insert(0, nivel_base)
    niveles = {}
    anterior = None
    for nvls in órden[::-1]:
        if isinstance(nvls, str):
            niveles[nvls] = Nivel(nombre=nvls, subniveles=anterior)
            anterior = niveles[nvls]
        else:
            for nvl in nvls:
                niveles[nvl] = Nivel(nombre=nvl, subniveles=anterior)
            anterior = [niveles[nv] for nv in nvls]

    dic_doc = {f[col_cód]: f for f in doc}
    quedan = list(dic_doc)
    lugares = {}
    for nvl, obj_nvl in niveles.items():
        for cód in list(quedan):
            lg = dic_doc[cód]
            if lg[nvl]:
                nmb = lg[nvl]
                subs = {s for c, s in lugares.items() if dic_doc[c][nvl] == cód}
                lugares[cód] = Lugar(nmb, nivel=obj_nvl, cód=cód, sub_lugares=subs)
                quedan.remove(cód)

    return Lugar(nombre=nombre, nivel=niveles[nivel_base], sub_lugares=lugares.values())
