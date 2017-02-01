import csv
import io
import json
import math as mat

import matplotlib.pyplot as dib
import numpy as np


class Geografía(object):
    def __init__(símismo, archivo, orden, col_cód):

        símismo.orden = orden

        símismo.árbol = {}

        símismo.árbol_inv = {}

        símismo.cód_a_lugar = {}

        símismo.leer_archivo(archivo=archivo, orden=orden, col_cód=col_cód)

    def lugares_en(símismo, cód_lugar, escala=None):
        """

        :param cód_lugar:
        :type cód_lugar:
        :param escala:
        :type escala:
        :return:
        :rtype: list[str]
        """

        d_lugar = símismo.cód_a_lugar[cód_lugar]
        escala_lugar = d_lugar['escala']

        if escala is None:
            l_códs = [x for x, d in símismo.árbol_inv.items() if d[escala_lugar] == cód_lugar]
        else:
            l_códs = [x for x, d in símismo.árbol_inv.items()
                      if d[escala_lugar] == cód_lugar and símismo.cód_a_lugar[x]['escala'] == escala]

        return l_códs

    def leer_archivo(símismo, archivo, orden, col_cód):

        símismo.árbol = {}

        with open(archivo, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            # Guardar la primera fila como nombres de columnas
            cols = next(l)

            try:
                i_cols = [cols.index(x) for x in orden]
            except ValueError:
                raise ValueError('Los nombres de las regiones en "orden" ({}) no concuerdan con los nombres en el'
                                 ' archivo ({}).'.format(', '.join(orden), ', '.join(cols)))
            try:
                in_col_cód = cols.index(col_cód)
            except ValueError:
                raise ValueError('La columna de código de región especificada ({}) no concuerda con los nombres de '
                                 'columnas del archivo ({}).'.format(col_cód, ', '.join(cols)))

            # Para cada fila que sigue en el csv...
            for f in l:
                dic = símismo.árbol
                cód = f[in_col_cód]

                for i, n in enumerate(i_cols):

                    if i == len(i_cols) - 1:
                        dic[f[n]] = cód

                    elif f[n] not in dic:
                        dic[f[n]] = {}

                    dic = dic[f[n]]

                símismo.árbol_inv[cód] = dict([(orden[k], f[j]) for k, j in enumerate(i_cols)])

                escala = orden[max([n for n, i in enumerate(i_cols) if f[i] != ''])]
                nombre = f[cols.index(escala)]
                símismo.cód_a_lugar[cód] = {'escala': escala, 'nombre': nombre}


class Datos(object):
    def __init__(símismo, archivo_csv, año=None, cód_lugar=None, col_año=None, col_cód_lugar=None, cód_vacío=''):
        """

        :param archivo_csv:
        :type archivo_csv: str

        :param año:
        :type año: int | float

        :param cód_lugar:
        :type cód_lugar: str

        :param cód_vacío:
        :type cód_vacío: list[int | float | str] | int | float | str

        """

        símismo.archivo_datos = archivo_csv

        símismo.datos = {}
        símismo.años = None  # type: np.array
        símismo.lugares = None  # type: np.array

        símismo.vars = []
        símismo.n_obs = None

        if type(cód_vacío) is list:
            símismo.cod_vacío = cód_vacío
        else:
            símismo.cod_vacío = [cód_vacío]

        if '' not in símismo.cod_vacío:
            símismo.cod_vacío.append('')

        símismo.cargar_datos()

        if año is not None:
            símismo.años = np.full(símismo.n_obs, año, dtype=float)
        elif col_año is not None:
            símismo.estab_col_año(col=col_año)

        if cód_lugar is not None:
            símismo.lugares = np.array([cód_lugar] * símismo.n_obs)
        elif col_cód_lugar is not None:
            símismo.estab_col_lugar(col=col_cód_lugar)

    def cargar_datos(símismo, archivo=None):
        """
        Cargar los nombres de los variables y  el no. de observaciones, no los datos sí mismos.

        :param archivo:
        :type archivo: str

        :return:
        :rtype: list
        """

        if archivo is not None:
            símismo.archivo_datos = archivo
        else:
            archivo = símismo.archivo_datos

        with open(archivo, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            # Guardar la primera fila como nombres de columnas
            símismo.vars = next(l)

            símismo.n_obs = len(list(l))

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

        try:
            if símismo.datos[var] is None:
                símismo._cargar_datos(var=var)
        except KeyError:
            raise ValueError('Nombre de variable "{}" erróneo.'.format(var))

        datos = símismo.datos[var]

        if tipo == 'percentil':
            lím = (np.percentile(datos, rango[0]), np.percentile(datos, rango[1]))
        elif tipo == 'valor':
            lím = rango
        else:
            raise ValueError

        índ_errores = np.where(np.logical_or(datos < lím[0], datos > lím[1]))

        datos[índ_errores] = np.nan

        return len(índ_errores)

    def datos_irreg(símismo, var):
        """
        Identifica datos irregulares.

        :param var:
        :type var: str

        :return:
        :rtype: np.ndarray
        """

        try:
            if símismo.datos[var] is None:
                símismo._cargar_datos(var=var)
        except KeyError:
            raise ValueError('Nombre de variable "{}" erróneo.'.format(var))

        datos = símismo.datos[var]

        q75, q25 = np.percentile(datos, [75, 25])
        riq = q75 - q25

        return datos[(datos < q25 - 1.5 * riq) | (datos > q75 + 1.5 * riq)]

    def estab_col_año(símismo, col):

        try:
            símismo._cargar_datos(var=col)
        except ValueError:
            raise ValueError('Nombre de columna de años "{}" erróneo.'.format(col))

        símismo.años = símismo.datos[col]

    def estab_col_lugar(símismo, col):
        try:
            símismo._cargar_datos(var=col)
        except ValueError:
            raise ValueError('Nombre de columna de códigos del lugar "{}" erróneo.'.format(col))
        símismo.lugares = símismo.datos[col]

    def buscar_datos(símismo, l_vars, años=None, cód_lugar=None):
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

        with open(símismo.archivo_datos, newline='') as d:

            l = csv.reader(d)  # El lector de csv

            valores = []  # Para guardar la lista de datos de cada línea

            # Saltar la primera fila como nombres de columnas
            next(l)

            # Para cada fila que sigue en el csv...
            for f in l:
                valores.append(f)

        for v in var:
            n = símismo.vars.index(v)

            # Poner np.nan donde faltan observaciones y convertir a una matriz numpy
            matr = np.array([x[n] if x[n] not in símismo.cod_vacío else np.nan for x in valores], dtype=np.str)

            símismo.datos[v] = matr.astype(np.float)

    def guardar_datos(símismo, archivo=None):
        """

        """

        if archivo is None:
            archivo = símismo.archivo_datos
        else:
            símismo.archivo_datos = archivo

        for var in símismo.vars:
            if símismo.datos[var] is None:
                símismo._cargar_datos(var)

        with open(símismo.archivo_datos, 'w', newline='') as d:
            e = csv.writer(d)
            e.writerow(símismo.vars)
            for i in range(símismo.n_obs):
                e.writerow([símismo.datos[x] for x in símismo.vars])


class DatosIndividuales(Datos):
    pass


class DatosRegión(Datos):

    def __init__(símismo, archivo_csv, año=None, cód_lugar=None, col_año=None, col_cód_lugar=None, cód_vacío='',
                 col_tmñ_muestra=None, col_error_est=None):

        super().__init__(archivo_csv, año, cód_lugar, col_año, col_cód_lugar, cód_vacío)

        símismo.tmñ_muestra = None

        símismo.error_est = None

        if col_tmñ_muestra is not None:
            símismo.estab_col_año(col=col_tmñ_muestra)

        if col_error_est is not None:
            símismo.estab_col_error(col=col_error_est)

    def estab_col_tmñ(símismo, col):

        try:
            símismo._cargar_datos(var=col)
        except ValueError:
            raise ValueError('Nombre de columna de tamaños de muestra "{}" erróneo.'.format(col))

        símismo.tmñ_muestra = símismo.datos[col]

    def estab_col_error(símismo, col):

        try:
            símismo._cargar_datos(var=col)
        except ValueError:
            raise ValueError('Nombre de columna de errores estándardes "{}" erróneo.'.format(col))

        símismo.error_est = símismo.datos[col]


class BaseDeDatos(object):

    def __init__(símismo, datos, geog, fuente=None):
        """

        :param datos:
        :type datos: list
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

    def graficar(símismo, var, escala='individual', años=None, cód_lugar=None, lugar=None, datos=None):

        dic_datos = símismo.pedir_datos(l_vars=[var], escala=escala, años=años,
                                        cód_lugar=cód_lugar, lugar=lugar, datos=datos)

        # El número máximo de años que tenga un lugar
        n_años = max([len(x['años']) for x in dic_datos.values()])

        if n_años > 1:
            for l in dic_datos:
                x = dic_datos[l]['años']
                y = dic_datos[l][var]

                q95, q75, q25, q05 = np.percentile(datos, [95, 75, 25, 5])

                dib.plot(x, y, color='green')
                dib.fill_between(x, q05, q25, facecolor='green', alpha=0.2)
                dib.fill_between(x, q75, q95, facecolor='green', alpha=0.2)
                dib.fill_between(x, q25, q75, facecolor='green', alpha=0.5)

            dib.show()
        else:
            datos_gráf_caja = [x['vars'][var] for x in dic_datos.values()]

            dib.boxplot(datos_gráf_caja)
            dib.xticks(range(1, len(dic_datos) + 1), [l for l in dic_datos])

            dib.show()

    def estimar(símismo, var, escala, años=None, lugar=None, cód_lugar=None, datos=None):

        datos = símismo.pedir_datos(l_vars=[var], escala=escala, años=años,
                                    cód_lugar=cód_lugar, lugar=lugar, datos=datos)

        promedio = np.nanmean(datos)
        error_estándar = np.nanstd(datos) / mat.sqrt(np.sum(np.isnan(datos)))

        return {'distr': 'Normal~([0], [1])'.format(promedio, error_estándar),
                'máx': promedio}

    def comparar(símismo, var_x, var_y, escala, años=None, cód_lugar=None, lugar=None, datos=None):

        d_datos = símismo.pedir_datos(l_vars=[var_x, var_y], escala=escala, años=años, cód_lugar=cód_lugar,
                                      lugar=lugar, datos=datos)

        datos_x = np.array([])
        datos_y = np.array([])

        for l in d_datos:
            datos_x = np.concatenate(datos_x, d_datos[l][var_x]['datos'])
            datos_y = np.concatenate(datos_y, d_datos[l][var_y]['datos'])

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

        if escala == 'individual':
            lugares = símismo.geog.lugares_en(cód_lugar=cód_lugar, escala=None)
        else:
            lugares = símismo.geog.lugares_en(cód_lugar=cód_lugar, escala=escala)

        dic = {}

        for c_l in lugares:
            dic_ind = {}
            for d in datos:
                if type(d) is DatosIndividuales:
                    símismo.combinar_dics(dic_ind, d.buscar_datos(l_vars=l_vars, años=años, cód_lugar=c_l))
                else:
                    if escala == 'individual':
                        # Si la escala es individual, no podemos hacer nada con datos regionales
                        pass
                    else:
                        símismo.combinar_dics(dic, d.buscar_datos(l_vars=l_vars, años=años, cód_lugar=cód_lugar))

            if escala == 'individual':
                símismo.combinar_dics(dic, dic_ind)
            else:
                símismo.combinar_dics(dic, símismo.combinar_por_año(dic_ind))

        return dic

    def combinar_dics(símismo, d1, d2):
        # Agrega d2 a d1, y, para matrices numpy, las concatena.
        for ll, v in d2.items():
            if ll not in d1:
                d1[ll] = v
            elif type(v) is dict:
                símismo.combinar_dics(d1=d1[ll], d2=v)
            elif type(v) is np.ndarray():
                d1[ll].concatenate(v)
            else:
                raise TypeError

    @staticmethod
    def combinar_por_año(d):
        # Combina todos los datos del mismo año (tomando el promedio.
        for l in d:
            for v in d[l]:
                datos = d[l][v]['datos']
                años = d[l][v]['años']

                años_únicos = np.unique(d[l][v]['años']).sort()
                datos_prom = np.array([np.nanmean(datos[np.where(años == x)]) for x in años_únicos])
                d[l][v] = {'datos': datos_prom, 'años': años_únicos}
        return d

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
