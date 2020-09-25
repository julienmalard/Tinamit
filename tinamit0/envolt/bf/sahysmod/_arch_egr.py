import re

import numpy as np


def leer_arch_egr(archivo, años=None, procesar=True):
    años = [años] if isinstance(años, int) else años

    dic_datos = {}

    n_est, n_polí = _buscar_forma(archivo)
    n_años = _buscar_n_años(archivo) if años is None else len(años)
    with open(archivo, 'r') as d:

        for a in _avanzar_año(d, año=años):

            for e in range(1, n_est + 1):
                _avanzar_a_estación(e, d)

                for p in range(1, n_polí + 1):
                    _avanzar_a_polígono(p, d)

                    f = d.readline()

                    while not _fin_sección(f):
                        vrs = _extraer_vars(f)
                        for var, val in vrs:
                            if var not in dic_datos:
                                dic_datos[var] = np.full((n_años, n_est, n_polí), np.nan)
                            if len(val):
                                dic_datos[var][a, e - 1, p - 1] = val.replace(',', '.')

                        f = d.readline()
    if procesar:
        procesar_cr(dic_datos)

    return dic_datos


def procesar_cr(dic):
    # Estos variables, si faltan en el egreso, deberían ser 0 y no NaN
    for cr in ['cra', 'crb', 'cru', 'cr4', 'a', 'b', 'u']:
        dic[cr][np.isnan(dic[cr])] = 0

    # Ajustar la salinidad por la presencia de varios cultivos
    kr = dic['kr']

    salin_suelo = np.zeros_like(kr)

    # Crear una máscara boleana para cada valor potencial de Kr y llenarlo con la salinidad correspondiente
    kr0 = (kr == 0)
    salin_suelo[kr0] = \
        dic['a'][kr0] * dic['cra'][kr0] + dic['b'][kr0] * dic['crb'][kr0] + dic['u'][kr0] * dic['cru'][kr0]

    kr1 = (kr == 1)
    salin_suelo[kr1] = dic['cru'][kr1] * dic['u'][kr1] + dic['c1*'][kr1] * (1 - dic['u'][kr1])

    kr2 = (kr == 2)
    salin_suelo[kr2] = dic['cra'][kr2] * dic['a'][kr2] + dic['c2*'][kr2] * (1 - dic['a'][kr2])

    kr3 = (kr == 3)
    salin_suelo[kr3] = dic['crb'][kr3] * dic['b'][kr3] + dic['c3*'][kr3] * (1 - dic['b'][kr3])

    kr4 = (kr == 4)
    salin_suelo[kr4] = dic['cr4'][kr4]

    para_llenar = [
        {'másc': kr0, 'cr': ['cr4']},
        {'másc': kr1, 'cr': ['cra', 'crb', 'cr4']},
        {'másc': kr2, 'cr': ['crb', 'cru', 'cr4']},
        {'másc': kr3, 'cr': ['cra', 'cru', 'cr4']},
        {'másc': kr4, 'cr': ['cra', 'crb', 'cru']}
    ]

    for d in para_llenar:
        l_cr = d['cr']
        másc = d['másc']

        for cr in l_cr:
            dic[cr][másc] = salin_suelo[másc]

    # Aseguarse que no quedamos con áreas que faltan
    for k in ["a", "b"]:
        dic[k][dic[k] == -1] = 0


def _buscar_forma(arch):
    n_est = n_polí = 0
    # para hacer: más elegante
    with open(arch, 'r') as d:
        f = d.readline()
        while not re.match(r'\W*YEAR:\W+0+\W', f):
            f = d.readline()

        while not re.match(r'\W*YEAR:\W+1+\W', f):
            m = re.search(r'\W*Season:\W+([0-9]+)\W', f)
            if m:
                n_est = int(m.groups()[0])
            else:
                m = re.search(r'\W*Polygon:\W+([0-9]+)\W', f)
                if m:
                    n_polí = int(m.groups()[0])
            f = d.readline()

    return n_est, n_polí


def _buscar_n_años(arch):
    n_años = 0
    with open(arch, 'r') as d:
        for f in d:
            m = re.search(r'\W*Polygon:\W+([0-9]+)\W', f)
            if m:
                n_años = int(m.groups()[0]) + 1

    return n_años


def _avanzar_año(d, año=None):
    f = d.readline()
    if año is None:
        while re.match(r'\W*YEAR:\W+[0-9]+\W', f) is None:
            f = d.readline()
        yield 0
    else:
        for i, a in enumerate(año):
            while re.match(r'\W*YEAR:\W+%i\W' % a, f) is None:
                f = d.readline()
            yield i


def _avanzar_a_estación(estación, d):
    f = d.readline()
    while re.match(r'\W*Season:\W+%i\W' % estación, f) is None:
        f = d.readline()


def _avanzar_a_polígono(polígono, d):
    f = d.readline()
    while re.match(r'\W*Polygon:\W+%i\W' % polígono, f) is None:
        f = d.readline()


def _fin_sección(f):
    return re.match(r' #$', f) is not None


def _extraer_vars(f):
    return [(vr.lower(), vl) for vr, vl in re.findall(r'([A-Za-z0-9*#]+)\W+=\W+([0-9.]+(?:E?[+\-0-9]+)?)?', f)]
