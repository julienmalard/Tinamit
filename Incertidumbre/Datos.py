import csv
import io
import json
import numpy as np

class Geografía(object):
    def __init__(símismo, escalas, orden):
        símismo.orden = orden

        símismo.árbol = {*[(x, {}) for x in escalas]}

        for n, escala in enumerate(orden):
            códs, noms, pars = leer(escalas[escala], cols=['código', 'lugar', 'pariente'], encabezadas=True)

            árbol = símismo.árbol[escala]

            for m, nom in enumerate(noms):
                árbol[m] = cód


class Datos(object):
    def __init__(símismo, archivo_csv, año=None):
        """

        :param archivo_csv:
        :type archivo_csv: str
        :param año:
        :type año: int | float

        """

        símismo.archivo_bd = archivo_csv

        símismo.datos = {}
        símismo.años = np.array([])

        símismo.vars = []
        símismo.n_obs = None

        símismo.cargar_bd()

        if año is not None:
            símismo.años = np.empty(símismo.n_obs)
            símismo.años[:] = año

    def cargar_bd(símismo, archivo=None):
        """
        Cargar los nombres de los variables y  el no. de observaciones, no los datos sí mismos.

        :param archivo:
        :type archivo: str

        :return:
        :rtype: list
        """

        if archivo is not None:
            símismo.archivo_bd = archivo
        else:
            archivo = símismo.archivo_bd

        with open(archivo, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            # Guardar la primera fila como nombres de columnas
            símismo.vars = next(l)
            símismo.n_obs = len(l)

        for var in símismo.vars:
            símismo.datos[var] = None

    def limpiar(símismo, var, rango, tipo='percentil'):
        """

        :param var:
        :type var: str

        :param rango:
        :type rango: tuple

        :param tipo:
        :type tipo: str

        """

        if símismo.datos[var] is None:
            símismo._cargar_datos(var=var)

        datos = símismo.datos[var]

        if tipo == 'percentil':
            lím = (np.percentile(datos, rango[0]), np.percentile(datos, rango[1]))
        elif tipo == 'valor':
            lím = rango
        else:
            raise ValueError

        datos[datos < lím[0] | datos > lím[1]] = np.nan

    def datos_irreg(símismo, var):
        """
        Identifica datos irregulares.

        :param var:
        :type var: str

        :return:
        :rtype: np.ndarray
        """

        if símismo.datos[var] is None:
            símismo._cargar_datos(var=var)

        datos = símismo.datos[var]

        q75, q25 = np.percentile(datos, [75, 25])
        riq = q75 - q25
        return datos[(datos < q25 - 1.5 * riq) | (datos > q75 + 1.5 * riq)]

    def estab_año(símismo, col):

        símismo._cargar_datos(var=col)
        símismo.años = símismo.datos[col]

    def _cargar_datos(símismo, var):
        """

        :param var:
        :type var: str | list

        """

        if type(var) is str:
            var = [var]

        with open(símismo.archivo_bd, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            valores = []  # Para guardar la lista de datos de cada línea

            # Saltar la primera fila como nombres de columnas
            next(l)

            # Para cada fila que sigue en el csv...
            for f in l:
                valores.append(f)

        for v in var:
            n = símismo.vars.index(v)

            matr = np.array([x[n] for x in valores])
            matr[matr == ''] = np.nan

            símismo.datos[v] = matr.astype(np.float)

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


class DatosIndividuales(Datos):

    def __init__(símismo, archivo_csv, año=None):
        """

        :param archivo_csv:
        :type archivo_csv: str
        :param año:
        :type año: int | float

        """

        super().__init__(archivo_csv=archivo_csv, año=año)


class DatosRegión(Datos):
    pass


class BaseDeDatos(object):

    def __init__(símismo, datos, geog, fuente=None):
        símismo.datos = datos
        símismo.geog = geog

        símismo.receta = {}

        símismo.fuente = fuente

    def guardar(símismo, archivo=None):

        if archivo is None:
            archivo = símismo.fuente

        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

    def cargar(símismo, fuente):

        with open(fuente, 'r', encoding='utf8') as d:
            nuevo_dic = json.load(d)

        símismo.receta.clear()
        símismo.receta.update(nuevo_dic)

        símismo.fuente = fuente
