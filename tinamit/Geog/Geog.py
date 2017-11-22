import datetime as ft
import os
import re
from warnings import warn as avisar

import matplotlib.pyplot as dib
from matplotlib import cm
import matplotlib.colors as colors

import numpy as np
import pandas as pd
import shapefile as sf

from taqdir.مقامات import مقام

# Ofrecemos la oportunidad de utilizar تقدیر, taqdir, en español
conv_vars = {
    'Precipitación': 'بارش',
    'Radiación solar': 'شمسی_تابکاری',
    'Temperatura máxima': 'درجہ_حرارت_زیادہ',
    'Temperatura promedia': 'درجہ_حرارت_کم',
    'Temperatura mínima': 'درجہ_حرارت_اوسط'
}


# Una subclase traducida
class Lugar(مقام):
    def __init__(símismo, lat, long, elev):

        super().__init__(lat=lat, long=long, elev=elev)

    def observar(símismo, archivo, datos, fecha=None, mes=None, año=None):
        super().cargar_datos(archivo=archivo, cols_datos=datos, fecha=fecha, mes=mes, año=año)

    def prep_datos(símismo, primer_año, último_año, rcp, n_rep=1, diario=True, mensual=True,
                   postdict=None, predict=None, regenerar=True):
        super().prep_datos(primer_año, último_año, rcp, n_rep=1, diario=True, mensual=True,
                           postdict=None, predict=None, regenerar=True)

    def comb_datos(símismo, vars_clima, combin, f_inic, f_final):
        """

        :param vars_clima:
        :type vars_clima: list[str]
        :param combin:
        :type combin: list[str]
        :param f_inic:
        :type f_inic: ft.datetime
        :param f_final:
        :type f_final: ft.datetime
        :return:
        :rtype: dict[np.ndarray]
        """

        bd = símismo.datos['diario']  # type: pd.DataFrame
        datos_interés = bd[vars_clima][(bd['دن'] >= f_inic) & (bd['دن'] <= f_final)]

        resultados = {}
        for v, c in zip(vars_clima, combin):
            try:
                v_conv = conv_vars[v]
            except KeyError:
                raise ValueError('El variable "{}" está erróneo. Debe ser uno de:\n'
                                 '\t{}'.format(v, ', '.join(conv_vars)))
            if c is None:
                if v in ['درجہ_حرارت_زیادہ', 'درجہ_حرارت_کم', 'درجہ_حرارت_اوسط']:
                    c = 'prom'
                else:
                    c = 'total'

            if c == 'prom':
                resultados[v] = datos_interés[v_conv].mean()
            elif c == 'total':
                resultados[v] = datos_interés[v_conv].sum()
            else:
                raise ValueError

        return resultados


class Geografía(object):
    def __init__(símismo, nombre):
        símismo.nombre = nombre
        símismo.regiones = {}
        símismo.objetos = {}

    def agregar_objeto(símismo, archivo, nombre=None, color='#000000', llenar=True):
        if nombre is None:
            nombre = os.path.splitext(os.path.split(archivo)[1])[0]

        símismo.objetos[nombre] = {'obj': sf.Reader(archivo),
                                   'color': color,
                                   'llenar': llenar}

    def agregar_regiones(símismo, archivo, col_orden=None):

        af = sf.Reader(archivo)

        if col_orden is not None:
            attrs = af.fields[1:]
            nombres_attr = [field[0] for field in attrs]
            try:
                orden = np.array([x.record[nombres_attr.index(col_orden)] for x in af.shapeRecords()])
            except ValueError:
                raise ValueError('La columna "{}" no existe en la base de datos.'.format(col_orden))

            orden -= np.min(orden)

        else:
            orden = range(len(af.records()))

        símismo.regiones = {'af': af, 'orden': orden}

    def dibujar(símismo, archivo, valores=None, título=None, unidades=None, colores=None, escala=None):
        """



        :param archivo:
        :type archivo: str
        :param valores:
        :type valores: np.ndarray
        :param título:
        :type título: str
        :param unidades:
        :type unidades: str
        :param colores:
        :type colores: str | list | tuple
        :param escala:
        :type escala: tuple

        """

        if colores is None:
            colores = ['#FF6666', '##FFCC66', '#00CC66']

        if isinstance(colores, str):
            colores = ['#FFFFFF', colores]
        elif isinstance(colores, tuple):
            colores = list(colores)

        dib.figure()
        ejes = dib.axes()
        ejes.set_aspect('equal')

        if valores is not None:
            regiones = símismo.regiones['af']
            orden = símismo.regiones['orden']

            n_regiones = len(regiones.shapes())
            if len(valores) != n_regiones:
                raise ValueError ('El número de regiones no corresponde con el tamñao de los valores.')

            if escala is None:
                escala = (np.min(valores), np.max(valores))
            if len(escala) != 2:
                raise ValueError

            vals_norm = (valores - escala[0]) / (escala[1] - escala[0])

            d_clrs = gen_d_mapacolores(colores=colores)

            mapa_color = colors.LinearSegmentedColormap('mapa_color', d_clrs)
            norm = colors.Normalize(vmin=escala[0], vmax=escala[1])
            cpick = cm.ScalarMappable(norm=norm, cmap=mapa_color)
            cpick.set_array([])

            v_cols = mapa_color(vals_norm)
            dibujar_shp(regiones, orden=orden, colores=v_cols)

            if unidades is not None:
                dib.colorbar(cpick, label=unidades)
            else:
                dib.colorbar(cpick)

        for nombre, d_obj in símismo.objetos.items():
            color = d_obj['color']
            llenar = d_obj['llenar']
            if color == 'agua':
                color = '#A5BFDD'
            elif color == 'calle':
                color = '#7B7B7B'
            elif color == 'ciudad':
                color = '#FB9A99'
            elif color == 'bosque':
                color = '#33A02C'
            elif not re.match('#?[0-9A-Fa-f]{6}$', color):
                color = '#000000'

            dibujar_shp(frm=d_obj['obj'], colores=color, llenar=llenar)

        if título is not None:
            dib.title(título)

        dib.savefig(archivo, dpi=500)
        dib.clf()


def dibujar_shp(frm, colores, orden=None, llenar=True):
    """

    Basado en código de Chris Halvin: https://github.com/chrishavlin/learning_shapefiles/tree/master/src

    :param frm:
    :type frm: sf.Reader

    :param colores:
    :type colores: str | list[str] | np.ndarray

    :param llenar:
    :type llenar: bool
    """

    n_formas = len(frm.shapes())

    if orden is not None:
        regiones = [x for _, x in sorted(zip(orden, frm.shapes()))]
    else:
        regiones = frm.shapes()

    if isinstance(colores, str) or isinstance(colores, tuple):
        colores = [colores]*n_formas
    else:
        if len(colores) != n_formas:
            raise ValueError

    for forma, col in zip(regiones, colores):
        n_puntos = len(forma.points)
        n_partes = len(forma.parts)

        if n_partes == 1:
            x_lon = np.zeros((len(forma.points), 1))
            y_lat = np.zeros((len(forma.points), 1))
            for ip in range(len(forma.points)):
                x_lon[ip] = forma.points[ip][0]
                y_lat[ip] = forma.points[ip][1]
            if llenar:
                dib.fill(x_lon, y_lat, color=col)
            else:
                dib.plot(x_lon, y_lat, color=col)

        else:
            for ip in range(n_partes):  # Para cada parte del imagen
                i0 = forma.parts[ip]
                if ip < n_partes - 1:
                    i1 = forma.parts[ip + 1] - 1
                else:
                    i1 = n_puntos

                seg = forma.points[i0:i1 + 1]
                x_lon = np.zeros((len(seg), 1))
                y_lat = np.zeros((len(seg), 1))
                for ip in range(len(seg)):
                    x_lon[ip] = seg[ip][0]
                    y_lat[ip] = seg[ip][1]

                if llenar:
                    dib.fill(x_lon, y_lat, color=col)
                else:
                    dib.plot(x_lon, y_lat, color=col)


def inter_color(colores, p, tipo='hex'):
    """

    :param colores:
    :type colores: list[str, str]
    :param p:
    :type p: float | int
    :param tipo:
    :type tipo: str
    :return:
    :rtype: str
    """
    colores = colores.copy()

    for i, c in enumerate(colores):
        if isinstance(c, str):
            colores[i] = tuple(int(c.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    def interpol(val1, val2, u):
        return int(val1 + (val2 - val1)*u)

    def interpol_col(col1, col2, u):
        return tuple([interpol(col1[n], col2[n], u) for n in range(3)])

    pos = p * (len(colores)-1)
    inic = max(0, int(pos) - 1)
    fin = inic + 1
    if fin >= len(colores):
        fin = len(colores) - 1
    col = interpol_col(colores[inic], colores[fin], u=pos)

    if tipo == 'rgb':
        col_final = col
    elif tipo == 'hex':
        col_final = '#%02x%02x%02x' % col
    else:
        raise KeyError

    return col_final


def hex_a_rva(hex):
    return tuple(int(hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


def gen_d_mapacolores(colores):
    clrs_rva = [hex_a_rva(x) for x in colores]
    n_colores = len(colores)

    dic_c = {'red': tuple((round(i / (n_colores - 1), 2), clrs_rva[i][0] / 255, clrs_rva[i][0] / 255) for i in
                          range(0, n_colores)),
             'green': tuple(
                 (round(i / (n_colores - 1), 2), clrs_rva[i][1] / 255, clrs_rva[i][1] / 255) for i in
                 range(0, n_colores)),
             'blue': tuple(
                 (round(i / (n_colores - 1), 2), clrs_rva[i][2] / 255, clrs_rva[i][2] / 255) for i in
                 range(0, n_colores))}

    return dic_c
