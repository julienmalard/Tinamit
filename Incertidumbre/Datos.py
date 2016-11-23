import csv
import io
import json
import numpy as np
import matplotlib.pyplot as dib

class Geografía(object):
    def __init__(símismo, archivo, orden, col_cód):

        símismo.orden = orden

        símismo.árbol = {}

        símismo.árbol_inv = {}

        símismo.leer_archivo(archivo=archivo, orden=orden, col_cód=col_cód)

    def leer_archivo(símismo, archivo, orden, col_cód):

        símismo.árbol = dict(*[(x, {}) for x in orden])

        with open(archivo, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            # Guardar la primera fila como nombres de columnas
            cols = next(l)

            i_cols = [cols.index(x) for x in orden]

            in_col_cód = cols.index(col_cód)

            # Para cada fila que sigue en el csv...
            for f in l:
                dic = símismo.árbol
                for i, n in enumerate(i_cols):

                    if i == len(i_cols) - 1:
                        dic[f[n]] = f[in_col_cód]
                        símismo.árbol_inv[f[in_col_cód]] = {*[(orden[k], f[j]) for k, j in enumerate(i_cols)]}

                    elif f[n] not in dic:
                        dic[f[n]] = {}
                        dic = dic[f[n]]


class Datos(object):
    def __init__(símismo, archivo_csv, año=None, cód_lugar=None, col_año=None, col_cód_lugar=None):
        """

        :param archivo_csv:
        :type archivo_csv: str
        :param año:
        :type año: int | float
        :param cód_lugar:
        :type cód_lugar: str

        """

        símismo.archivo_bd = archivo_csv

        símismo.datos = {}
        símismo.años = np.array([])
        símismo.lugares = []

        símismo.vars = []
        símismo.n_obs = None

        símismo.cargar_bd()

        if año is not None:
            símismo.años = np.empty(símismo.n_obs)
            símismo.años[:] = año
        elif col_año is not None:
            símismo.estab_año(col=col_año)

        if cód_lugar is not None:
            símismo.lugares = [cód_lugar] * símismo.n_obs
        elif col_cód_lugar is not None:
            símismo.estab_lugar(col=col_cód_lugar)

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

    def estab_lugar(símismo, col):

        símismo._cargar_datos(var=col)
        símismo.lugares = símismo.datos[col]

    def buscar_datos(símismo, l_vars, años=None, cód_lugar=None, ):
        """

        :param l_vars:
        :type l_vars: list

        :param años:
        :type años: tuple

        :param cód_lugar:
        :type cód_lugar: list

        :return:
        :rtype: dict

        """

        # Si no se especificó lugar, tomar todos los lugares disponibles
        if cód_lugar is None:
            cód_lugar = set(símismo.lugares)

        if años is None:
            años = (-np.inf, np.inf)

        if años[0] is None:
            años = (-np.inf, años[1])
        if años[1] is None:
            años = (años[0], np.inf)

        if type(l_vars) is not list:
            l_vars = [l_vars]

        for var in l_vars:
            if símismo.datos[var] is None:
                símismo._cargar_datos(var)

        dic = {}

        for l in cód_lugar:
            dic[l] = {}

            disp = [np.where((símismo.lugares == l) & (símismo.años >= años[0]) & (símismo.años <= años[1])
                             & (símismo.datos[v] != np.nan))
                    for v in l_vars]
            índ = np.all(disp, axis=0)

            for var in l_vars:
                if var not in dic:
                    dic[var] = {}

                dic[var][l]['datos'] = símismo.datos[var][índ]
                dic[var][l]['años'] = símismo.años[índ]

        return dic

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
            if símismo.datos[var] is None:
                símismo._cargar_datos(var)

        with open(símismo.archivo_bd, 'w', newline='') as d:
            e = csv.writer(d)
            e.writerow(símismo.vars)
            for i in range(símismo.n_obs):
                e.writerow([símismo.datos[x] for x in símismo.vars])


class DatosIndividuales(Datos):

    def __init__(símismo, archivo_csv, año=None, cód_lugar=None, col_año=None, col_cód_lugar=None):
        """

        :param archivo_csv:
        :type archivo_csv: str
        :param año:
        :type año: int | float

        """

        super().__init__(archivo_csv=archivo_csv, año=año, cód_lugar=cód_lugar,
                         col_año=col_año, col_cód_lugar=col_cód_lugar)


class DatosRegión(Datos):
    pass


class BaseDeDatos(object):

    def __init__(símismo, datos, geog, fuente=None):
        """

        :param datos:
        :type datos: list | Datos
        :param geog:
        :type geog: Geografía
        :param fuente:
        :type fuente: str
        """

        if type(datos) is Datos:
            datos = [datos]

        símismo.datos = datos
        símismo.geog = geog

        símismo.receta = {}

        símismo.fuente = fuente

    def renombrar_var(símismo, var, nuevo_nombre, datos=None):

        if datos is None:
            datos = símismo.datos

        if type(datos) is not list:
            datos = [datos]

        for d in datos:
            d.vars[d.vars.index(var)] = nuevo_nombre
            d.datos[nuevo_nombre] = d.datos[var]
            d.datos.pop(var)

    def graficar(símismo, var, años=None, cód_lugar=None, lugar=None, datos=None):

        dic_datos = símismo.pedir_datos(l_vars=[var], años=años, cód_lugar=cód_lugar, lugar=lugar, datos=datos)[var]

        n_años =

        if n_años > 1:
            for l in dic_datos:
                pass
                # para hacer: dibujar gráfico

    def estimar(símismo, var, escala, años=None, lugar=None, cód_lugar=None):


    def comparar(símismo, var_x, var_y, escala, años=None, cód_lugar=None, lugar=None, datos=None):

        d_datos = símismo.pedir_datos(l_vars=[var_x, var_y], escala=escala, años=años, cód_lugar=cód_lugar,
                                      lugar=lugar, datos=datos)

        d_datos_x = d_datos[var_x]
        d_datos_y = d_datos[var_y]

        datos_x = np.array([])
        datos_y = np.array([])

        for l in d_datos_x:
            datos_x = np.concatenate(datos_x, d_datos_x[l]['datos'])
            datos_y = np.concatenate(datos_y, d_datos_y[l]['datos'])

        dib.plot(datos_x, datos_y)

    def pedir_datos(símismo, l_vars, escala='individual', años=None, cód_lugar=None, lugar=None, datos=None):
        """

        :param l_vars:
        :type l_vars: list

        :param escala:
        :type escala: str

        :param años:
        :type años: tuple

        :param cód_lugar:
        :type cód_lugar: str

        :param lugar:
        :type lugar: list

        :param datos:
        :type datos: list

        :return:
        :rtype: dict

        """

        if escala not in (símismo.geog.órden + ['individual']):
            raise ValueError

        if cód_lugar is not None and lugar is not None:
            raise ValueError('No se puede especificar y un código de lugar, y el lugar. Hay que usar o el uno,'
                             'o el otro para identificar el lugar.')

        # Convertir una ubicación de lugar (lista) a código de lugar
        if lugar is not None:
            dic = símismo.geog.árbol
            dif = len(símismo.geog.órden) - len(lugar)
            lugar += [''] * dif

            for l in lugar:
                dic = dic[l]

            cód_lugar = dic

        if type(cód_lugar) is not list:
            cód_lugar = [cód_lugar]

        if datos is None:
            datos = símismo.datos

        if type(datos) is not list:
            datos = [datos]

        # Agrega d2 a d1, y, para matrices numpy, las concatena.
        def combinar_dics(d1, d2):
            for ll, v in d2.items():
                if ll not in d1:
                    d1[ll] = v
                elif type(v) is dict:
                    combinar_dics(d1=d1[ll], d2=v)
                elif type(v) is np.ndarray():
                    d1[ll].concatenate(v)
                else:
                    raise TypeError

        def lugares_en(cód_lugar, árbol, árbol_inv, orden):
            try:
                nivel = orden(min([orden.index(ll) for ll, v in árbol_inv[cód_lugar] if v == '']))
            except ValueError:
                nivel = orden[-1]

            ubic = []  #

            dic = árbol
            for u in ubic:
                dic = dic[u]

            faltan = orden[orden.index(nivel):]
            for f in faltan:


            return l_cód_lugares

        if escala == 'individual':
            lugares = lugares_en(cód_lugar, símismo.geog.árbol, símismo.geog.árbol_inv, símismo.geog.orden)
        else:
            lugares =

        dic = {}

        for c_l in lugares:
            for d in datos:
                combinar_dics(dic, d.buscar_datos(l_vars=l_vars, años=años, cód_lugar=cód_lugar))

        return dic

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
