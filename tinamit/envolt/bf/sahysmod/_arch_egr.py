import re

import numpy as np


def leer_arch_egr(archivo, n_est, n_polí, años):
    años = [años] if isinstance(años, int) else años

    dic_datos = {}
    for k, v in dic_datos.items():
        v[:] = -1

    with open(archivo, 'r') as d:

        for a in años:
            _avanzar_a_año(a, d)

            for e in range(n_est):
                _avanzar_a_estación(e, d)

                for p in range(n_polí):
                    _avanzar_a_polígono(p, d)

                    f = d.readline()

                    while not _fin_sección(f):

                        for var, val in _extraer_vars(f):
                            if var not in dic_datos:
                                dic_datos[var] = np.full((len(años), n_est, n_polí), np.nan)
                            if len(val):
                                dic_datos[var][a, e, p] = val

                        f = d.readline()

    return dic_datos


def _avanzar_a_año(año, d):
    f = d.readline()
    while re.match(r'\W*YEAR:\W+%i\W' % año, f) is None:
        f = d.readline()


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
    return re.search(r'([A-Za-z0-9*#]+)\W+=\W+([0-9.E\-]+)?', f)
