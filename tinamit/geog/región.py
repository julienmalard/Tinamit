import csv
import os
from collections import OrderedDict

from tinamit.config import _
from tinamit.cositas import detectar_codif


class Nivel(object):
    def __init__(símismo, nombre, subniveles=None):
        símismo.nombre = nombre
        símismo.subniveles = subniveles

    def __eq__(símismo, otro):
        return str(símismo) == str(otro)

    def __str__(símismo):
        return símismo.nombre


class Lugar(object):
    def __init__(símismo, nombre, nivel, cód=None, sub_lugares=None):
        símismo.cód = cód or nombre
        símismo.nivel = nivel
        símismo.nombre = nombre
        símismo.sub_lugares = set(sub_lugares or [])

    def lugares(símismo, en=None, nivel=None):
        if en is None:
            buscar_en = símismo
        else:
            buscar_en = símismo[en]
        return {lg for lg in buscar_en if (nivel is None or lg.nivel == nivel)}

    def buscar_nombre(símismo, nombre, nivel=None):
        for lg in símismo:
            if lg.nombre == nombre and (nivel is None or lg.nivel == nivel):
                return lg
        raise ValueError(_('Lugar "{nmb}" no encontrado en "{lg}"').format(nmb=nombre, lg=símismo))

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



def gen_nivel(archivo, nivel_base, nombre=None, col_cód='Código'):
    codif_csv = detectar_codif(archivo)
    nombre = nombre or os.path.splitext(os.path.split(nombre)[1])[0]

    with open(archivo, newline='', encoding=codif_csv) as d:

        f = csv.DictReader(d)  # El lector de csv

        # Guardar la primera fila como nombres de columnas
        cols = [x.lower().strip() for x in f.fieldnames]

        if col_cód not in cols:
            raise ValueError(_(
                'La columna de código de región especificada ("{}") no concuerda con los nombres de '
                'columnas del csv ({}).'
            ).format(col_cód, ', '.join(cols)))

        doc = [OrderedDict((ll.lower().strip(), v.strip()) for ll, v in f.items()) for f in f]

    lugar_base = Lugar(nombre, )
    return Nivel(nombre=nivel_base, lugares=lugar_base)

    # Inferir el orden de la jerarquía
    órden = []

    escalas = [x for x in cols if x != col_cód]
    símismo.escalas.extend(escalas)

    símismo.info_geog.update({esc: [] for esc in escalas})

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

    símismo.orden_jerárquico.extend(órden)

    for f in doc:
        cód = f[col_cód]
        escala = None
        for esc in órden[::-1]:
            if isinstance(esc, str):
                if len(f[esc]):
                    escala = esc
            else:
                for nv_ig in esc:
                    if len(f[nv_ig]):
                        escala = nv_ig
            if escala is not None:
                break

        nombre = f[escala]

        símismo.cód_a_lugar[cód] = {
            'escala': escala,
            'nombre': nombre,
            'en': {ll: v for ll, v in f.items() if ll in escalas and len(v) and ll != escala}
        }
        símismo.info_geog[escala].append(cód)

    for cód, dic in símismo.cód_a_lugar.items():
        for esc, lg_en in dic['en'].items():
            if lg_en not in símismo.cód_a_lugar:
                dic['en'][esc] = símismo.nombre_a_cód(nombre=lg_en, escala=esc)
