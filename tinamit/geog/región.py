import csv
import os
from collections import OrderedDict

from tinamit.config import _
from tinamit.cositas import detectar_codif


class Región(object):
    def __init__(símismo, niveles):
        símismo.niveles = {n.nombre: n for n in niveles}

    def lugares_en(símismo, en, nivel):
        return símismo[nivel].lugares()

    def __getitem__(símismo, itema):
        return símismo.niveles[itema]


class Nivel(object):
    def __init__(símismo, nombre):
        símismo.nombre = nombre


class Lugar(object):
    def __init__(símismo, nombre, sub_lugares=None):
        símismo.nombre = nombre
        símismo.sub_lugares = sub_lugares or set()


class Forma(object):
    pass

def región_de_csv(archivo, col_cód='Código'):
    codif_csv = detectar_codif(archivo)
    ext = os.path.splitext(archivo)[1]

    if ext != '.csv':
        raise ValueError(_('El archivo debe ser de formato csv.'))

    with open(archivo, newline='', encoding=codif_csv) as d:

        l = csv.DictReader(d)  # El lector de csv

        # Guardar la primera fila como nombres de columnas
        cols = [x.lower().strip() for x in l.fieldnames]

        if col_cód not in cols:
            raise ValueError(_(
                'La columna de código de región especificada ("{}") no concuerda con los nombres de '
                'columnas del csv ({}).'
            ).format(col_cód, ', '.join(cols)))

        doc = [OrderedDict((ll.lower().strip(), v.strip()) for ll, v in f.items()) for f in l]

    return Región()

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
