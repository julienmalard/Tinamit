import datetime as ft
import os
import re

import matplotlib.pyplot as dib
from matplotlib import cm
import matplotlib.colors as colors

import numpy as np
import pandas as pd
import shapefile as sf

from taqdir.مقام import مقام
from taqdir.ذرائع.مشاہدات import دن_مشا, مہنہ_مشا, سال_مشا

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

        super().__init__(چوڑائی=lat, طول=long, بلندی=elev)

    def observar_diarios(símismo, archivo, cols_datos, fecha):

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}

        obs = دن_مشا(archivo=archivo, c_fecha=fecha, cols_datos=d_cols)

        símismo.مشاہدہ_کرنا(مشاہد=obs)

    def observar_mensuales(símismo, archivo, cols_datos, meses, años):

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}

        obs = مہنہ_مشا(archivo=archivo, cols_datos=d_cols, c_meses=meses, c_años=años)

        símismo.مشاہدہ_کرنا(obs)

    def observar_anuales(símismo, archivo, cols_datos, años):

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}

        obs = سال_مشا(archivo=archivo, cols_datos=d_cols, c_años=años)
        símismo.مشاہدہ_کرنا(obs)

    def prep_datos(símismo, fecha_inic, fecha_final, rcp, prefs=None, lím_prefs=False, regenerar=True):
        super().اعداد_تیاری(fecha_inic, fecha_final, rcp, n_rep=1,
                            ترجیحات=prefs, lím_prefs=lím_prefs, regenerar=regenerar)

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

        bd = símismo.اعداد_دن  # type: pd.DataFrame
        datos_interés = bd.loc[f_inic:f_final]

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

    def agregar_objeto(símismo, archivo, nombre=None, tipo=None, alpha=None, color=None, llenar=None):
        if nombre is None:
            nombre = os.path.splitext(os.path.split(archivo)[1])[0]

        símismo.objetos[nombre] = {'obj': sf.Reader(archivo),
                                   'color': color,
                                   'llenar': llenar,
                                   'alpha': alpha,
                                   'tipo': tipo}

    def agregar_regiones(símismo, archivo, col_orden=None):

        af = sf.Reader(archivo)

        if col_orden is not None:
            attrs = af.fields[1:]
            nombres_attr = [field[0] for field in attrs]
            try:
                orden = np.array([x.record[nombres_attr.index(col_orden)] for x in af.shapeRecords()])
            except ValueError:
                raise ValueError('La columna "{}" no existe en la base de اعداد_دن.'.format(col_orden))

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
                raise ValueError('El número de regiones no corresponde con el tamñao de los valores.')

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

            tipo = d_obj['tipo']

            for a in ['color', 'llenar', 'alpha']:
                if d_obj[a] is None:
                    d_obj[a] = formatos_auto(a, tipo)

            color = d_obj['color']
            llenar = d_obj['llenar']
            alpha = d_obj['alpha']

            dibujar_shp(frm=d_obj['obj'], colores=color, alpha=alpha, llenar=llenar)

        if título is not None:
            dib.title(título)

        dib.savefig(archivo, dpi=500)
        dib.close()


def dibujar_shp(frm, colores, orden=None, alpha=1.0, llenar=True):
    """

    Basado en código de Chris Halvin: https://github.com/chrishavlin/learning_shapefiles/tree/master/src

    :param frm:
    :type frm: sf.Reader

    :param colores:
    :type colores: str | list[str] | np.ndarray

    :param orden:
    :type orden: np.ndarray | list

    :param alpha:
    :type alpha: float | int

    :param llenar:
    :type llenar: bool
    """

    n_formas = len(frm.shapes())

    if orden is not None:
        regiones = [x for _, x in sorted(zip(orden, frm.shapes()))]
    else:
        regiones = frm.shapes()

    if isinstance(colores, str) or isinstance(colores, tuple):
        colores = [colores] * n_formas
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
                dib.fill(x_lon, y_lat, color=col, alpha=alpha)
            else:
                dib.plot(x_lon, y_lat, color=col, alpha=alpha)

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
                for i in range(len(seg)):
                    x_lon[i] = seg[i][0]
                    y_lat[i] = seg[i][1]

                if llenar:
                    dib.fill(x_lon, y_lat, color=col, alpha=alpha)
                else:
                    dib.plot(x_lon, y_lat, color=col, alpha=alpha)


def hex_a_rva(hx):
    return tuple(int(hx.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


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


def formatos_auto(a, tipo):
    """

    :param a:
    :type a: str
    :param tipo:
    :type tipo: str
    :return:
    :rtype: str | bool | float
    """

    d_formatos = {
        'agua': {'color': '#A5BFDD',
                 'llenar': True,
                 'alpha': 0.5},
        'calle': {'color': '#7B7B7B',
                  'llenar': False,
                  'alpha': 1.0},
        'ciudad': {'color': '#FB9A99',
                   'llenar': True,
                   'alpha': 1.0},
        'bosque': {'color': '#33A02C',
                   'llenar': True,
                   'alpha': 0.7},
        'otro': {'color': '#FFECB3',
                 'llenar': False,
                 'alpha': 1.0}
    }

    if tipo is None or tipo not in d_formatos:
        tipo = 'otro'

    return d_formatos[tipo.lower()][a.lower()]
