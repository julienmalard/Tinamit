import csv


class Geografía(object):
    def __init__(símismo, escalas, orden):
        símismo.orden = orden

        símismo.árbol = {*[(x, {}) for x in escalas]}

        for n, escala in enumerate(orden):
            códs, noms, pars = leer(escalas[escala], cols=['código', 'lugar', 'pariente'], encabezadas=True)

            árbol = símismo.árbol[escala]

            for m, nom in enumerate(noms):
                árbol[m] = cód


class DatosIndividuales(object):

    def __init__(símismo, archivo_csv, año=None):
        """

        :param archivo_csv:
        :type archivo_csv: str
        :param año:
        :type año: int | float

        """

        símismo.archivo_bd = archivo_csv
        símismo.datos = {}

        símismo.vars = []
        símismo.n_obs = None

        símismo.cargar_bd()

    def cargar_bd(símismo, archivo=None):
        """

        :param archivo:
        :type archivo: str

        :return:
        :rtype: list
        """

        if archivo is not None:
            símismo.archivo_bd = archivo
        else:
            archivo = símismo.archivo_bd

        with open(símismo.archivo_bd, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            # Guardar la primera fila como nombres de columnas
            símismo.vars = next(l)
            símismo.n_obs = len(l)

        for var in símismo.vars:
            símismo.datos[var] = None

    def _cargar_datos(símismo, var):
        """

        :param var:
        :type var: str | list

        """

        if type(var) is str:
            var = [var]

        datos = dict([(x, None) for x in var])

        with open(símismo.archivo_bd, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            valores = []  # Para guardar la lista de datos de cada línea

            # Saltar la primera fila como nombres de columnas
            next(l)

            # Para cada fila que sigue en el csv...
            for f in l:
                for v in var:
                    datos[v] = [x[n] for x in valores]

    def guardar_datos(símismo):
        """

        """

        for var in símismo.vars:
            símismo._cargar_datos(var)

        with open(símismo.archivo_bd, 'w', newline='') as d:
            e = csv.writer(d)
            e.writerow(símismo.vars)
            for i in range(símismo.n_obs):
                e.writerow([símismo.datos[x] for x in símismo.vars])
