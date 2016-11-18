

class Geografía(object):
    def __init__(símismo, escalas, orden):
        símismo.orden = orden

        símismo.árbol = {*[(x, {}) for x in escalas]}

        for n, escala in enumerate(orden):
            códs, noms, pars = leer(escalas[escala], cols=['código', 'lugar', 'pariente'], encabezadas=True)

            árbol = símismo.árbol[escala]

            for m, nom in enumerate(noms):
                árbol[m] = cód


class DatosIndividuales():