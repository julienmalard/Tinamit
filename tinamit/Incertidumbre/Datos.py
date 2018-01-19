import csv
import datetime as ft
import json
import math as mat
import os
from warnings import warn as avisar

import matplotlib.pyplot as dib
import numpy as np
import pandas as pd

from Incertidumbre.Números import tx_a_núm
from tinamit import _


class Datos(object):
    def __init__(símismo, nombre, archivo, fecha, lugar, cód_vacío=''):
        """

        :param nombre:
        :type nombre: str

        :param archivo:
        :type archivo: str

        :param fecha:
        :type fecha: str | ft.date | ft.datetime | int

        :param ar:
        :type año: int | float

        :param lugar:
        :type lugar: str

        :param cód_vacío:
        :type cód_vacío: list[int | float | str] | int | float | str

        """

        símismo.nombre = nombre

        símismo.archivo_datos = archivo
        símismo.bd = _gen_bd(archivo)

        símismo.cols = símismo.bd.obt_nombres_cols()

        if fecha in símismo.cols:
            símismo.fechas = símismo.bd.obt_fechas(fecha)
        elif isinstance(fecha, ft.date) or isinstance(fecha, ft.datetime):
            símismo.fechas = fecha
        elif isinstance(fecha, int):
            símismo.fechas = ft.date(year=fecha, month=1, day=1)
        else:
            raise TypeError('')

        if lugar in símismo.cols:
            símismo.lugares = símismo.bd.obt_datos_tx(cols=lugar)
        else:
            símismo.lugares = str(lugar)

        if isinstance(cód_vacío, list):
            símismo.cod_vacío = set(cód_vacío)
        else:
            símismo.cod_vacío = {cód_vacío}

        símismo.cod_vacío.add('')

        símismo.n_obs = símismo.bd.n_obs

    def obt_datos(símismo, l_vars, cód_vacío=None):
        """

        :param l_vars:
        :type l_vars: list

        :param cód_vacío:
        :type cód_vacío: str | int | float | list | set

        :return:
        :rtype: dict

        """
        datos = símismo.bd.obt_datos(l_vars)

        códs_vacío = símismo.cod_vacío.copy()
        if cód_vacío is not None:
            if isinstance(cód_vacío, list) or isinstance(cód_vacío, set):
                códs_vacío.update(cód_vacío)
            else:
                códs_vacío.add(cód_vacío)

        for c in códs_vacío:
            datos[datos==c] = np.nan

        return datos


class DatosIndividuales(Datos):
    pass


class DatosRegión(Datos):

    def __init__(símismo, nombre, archivo, fecha, lugar, cód_vacío='', col_tmñ_muestra=None):

        super().__init__(nombre=nombre, archivo=archivo, fecha=fecha, lugar=lugar, cód_vacío=cód_vacío)

        if col_tmñ_muestra in símismo.cols:
            símismo.col_tmñ_muestra = col_tmñ_muestra
        else:
            raise ValueError(_('Nombre de columna de tamaños de muestra "{}" erróneo.').format(col_tmñ_muestra))


class SuperBD(object):

    def __init__(símismo, nombre, bds=None, geog=None):
        """

        :param nombre:
        :type nombre: str
        :param bds:
        :type bds: list | Datos
        """

        símismo.nombre = nombre
        símismo.geog = geog

        if bds is None:
            símismo.bds = {}  # type: dict[Datos]
        else:
            if isinstance(bds, Datos):
                bds = [bds]
            if isinstance(bds, list):
                símismo.bds = {d.nombre: d for d in bds}  # type: dict[Datos]
            else:
                raise TypeError('')

        símismo.vars = {}
        símismo.ind_a_reg = {}

        símismo.datos_reg = None  # type: pd.DataFrame
        símismo.datos_ind = None  # type: pd.DataFrame
        símismo._gen_bd_intern()

    def agregar_datos(símismo, bd, como=None, auto_llenar=True):
        """

        :param bd:
        :type bd: Datos
        :param como:
        :type como: str | list[str] | Datos
        :param auto_llenar:
        :type auto_llenar: bool

        """

        if bd in símismo.bds:
            avisar(_('Ya existía la base de datos "{}". Borramos la que estaba antes.').format(bd))

        símismo.bds[bd.nombre] = bd

        if auto_llenar:
            símismo.auto_llenar(bd=bd, como=como)

    def auto_llenar(símismo, bd, como):
        if como is None:
            como = [x for x in símismo.bds if x != bd]
        if not isinstance(como, list):
            como = [como]

        for var, d_var in símismo.vars.items():
            for b in d_var['fuente']:
                if b in como:
                    if isinstance(b, Datos):
                        b = b.nombre
                    var_bd = d_var['fuente'][b]['var_bd']
                    cód_vacío = d_var['fuente'][b]['cód_vacío']
                    if var_bd in bd.cols:
                        d_var['fuente'][bd.nombre] = {'var_bd': var_bd, 'cód_vacío': cód_vacío}
                        continue

                    else:
                        avisar(_('El variable existente "{}" no existe en la nueva base de datos "{}". No'
                                 'lo podremos copiar.').format(var_bd, bd.nombre))
        símismo._gen_bd_intern()

    def desconectar_datos(símismo, bd):

        if isinstance(bd, Datos):
            bd = bd.nombre

        if bd not in símismo.bds:
            raise ValueError('')

        símismo.bds.pop(bd)
        for var, d_var in símismo.vars.items():
            try:
                d_var['fuente'].pop(bd)
            except KeyError:
                pass

        símismo._limp_vars()

    def espec_var(símismo, var, var_bd=None, bds=None, cód_vacío=''):

        if var_bd is None:
            var_bd = var

        if bds is None:
            bds = list(símismo.bds)
        if not isinstance(bds, list):
            bds = [bds]
        for í, bd in enumerate(bds.copy()):
            if isinstance(bd, Datos):
                bds[í] = bd.nombre
            elif isinstance(bd, str):
                pass
            else:
                raise TypeError

        for nm_bd in bds:
            bd = símismo.bds[nm_bd]

            if var_bd not in bd.cols():
                avisar(_('"{}" no existe en base de datos "{}".').format(var_bd, nm_bd))

            datos = bd.obt_datos(l_vars=var, cód_vacío=cód_vacío)
            if isinstance(bd, DatosIndividuales):
                datos_ind = símismo.datos_ind
                datos_ind[var][datos_ind['bd'] == nm_bd] = datos
            else:
                datos_reg = símismo.datos_reg
                datos_reg[var][datos_reg['bd'] == nm_bd] = datos

        if var not in símismo.vars:
            símismo.vars[var] = {'fuente': {}, 'limp': {}}
        símismo.vars[var] = {'fuente': {bd.nombre: {'var': var_bd, 'cód_vacío': cód_vacío} for bd in bds}}

        símismo._gen_bd_intern()

    def borrar_var(símismo, var, bds=None):

        if var not in símismo.vars:
            raise ValueError('')

        if bds is None:
            símismo.vars.pop(var)
        else:
            if not isinstance(bds, list):
                bds = [bds]
            for bd in bds:
                if isinstance(bd, Datos):
                    bd = bd.nombre
                símismo.vars[var]['fuente'].pop(bd)

        símismo._limp_vars()

    def renombrar_var(símismo, var, nuevo_nombre):

        if var not in símismo.vars:
            raise ValueError('')
        if nuevo_nombre in símismo.vars:
            raise ValueError(_('El variable "{}" ya existe. Hay que borrarlo primero.').format(nuevo_nombre))

        símismo.vars[nuevo_nombre] = símismo.vars.pop(var)

        if var in símismo.datos_ind:
            símismo.datos_ind[nuevo_nombre] = símismo.datos_ind[var]
            símismo.datos_ind.drop(var, axis=1)

        if var in símismo.datos_reg:
            símismo.datos_reg[nuevo_nombre] = símismo.datos_reg[var]
            símismo.datos_reg.drop(var, axis=1)

    def espec_ind_a_reg(símismo, var, combin='prom'):

        if combin.lower() not in ['prom', 'suma']:
            raise ValueError('')
        
        símismo.ind_a_reg[var] = {'combin': combin}

        símismo._gen_bd_intern()

    def _limp_vars(símismo):

        # Asegurarse que no queden variables sin bases de datos en símismo.vars
        for v in list(símismo.vars.keys()):
            d_v = símismo.vars[v]
            if len(d_v['fuente']) == 0:
                símismo.vars.pop(v)

        datos_ind = símismo.datos_ind
        datos_reg = símismo.datos_reg

        # Asegurarse que no queden variables (columas) en las bases de datos que no estén en símismo.vars
        for bd_pd in [datos_ind, datos_reg]:
            if bd_pd:
                cols = list(bd_pd)
                for c in cols:
                    if c not in símismo.vars:
                        bd_pd.drop(c, axis=1, inplace=True)

        # Quitar observaciones en bases de datos que ya no están vinculadas
        if símismo.datos_ind:
            símismo.datos_ind = datos_ind[datos_ind['bd'].isin(símismo.bds)]
        if símismo.datos_reg:
            símismo.datos_reg = datos_reg[datos_reg['bd'].isin(símismo.bds)]

    def _gen_bd_intern(símismo):

        símismo._limp_vars()
        símismo.datos_ind = símismo.datos_reg = None

        # Agregar datos
        for nb, bd in símismo.bds.items():
            # Datos individuales
            if isinstance(bd, DatosIndividuales):
                vars_interés = [it for it in símismo.vars.items() if nb in it[1]['fuente']]
                if len(vars_interés):
                    datos_bd = np.array([bd.obt_datos(d_v['fuente'][nb]['var'], cód_vacío=d_v['fuente'][nb]['cód_vacío'])
                                         for v, d_v in vars_interés]).T

                    bd_pds_temp = pd.DataFrame(datos_bd, columns=[it[0] for it in vars_interés])

                    bd_pds_temp['bd'] = nb
                    bd_pds_temp['lugar'] = bd.lugares

                    if isinstance(bd.fechas, tuple):
                        bd_pds_temp['fecha'] = pd.to_datetime(bd.fechas[0]) + pd.to_timedelta([1,2,3], unit='day')
                    else:
                        bd_pds_temp['fecha'] = pd.to_datetime(bd.fechas)

                    if símismo.datos_ind is None:
                        símismo.datos_ind = bd_pds_temp
                    else:
                        símismo.datos_ind.append(bd_pds_temp, ignore_index=True)

            # Datos regionales
            else:
                vars_interés = [it for it in símismo.vars.items() if nb in it[1]['fuente']]
                if len(vars_interés):
                    datos_bd = np.array(
                        [bd.obt_datos(d_v['fuente'][nb]['var'], cód_vacío=d_v['fuente'][nb]['cód_vacío'])
                         for v, d_v in vars_interés]
                    ).T

                    bd_pds_temp = pd.DataFrame(datos_bd, columns=[it[0] for it in vars_interés])

                    bd_pds_temp['bd'] = nb
                    bd_pds_temp['lugar'] = bd.lugares

                    if isinstance(bd.fechas, tuple):
                        bd_pds_temp['fecha'] = pd.to_datetime(bd.fechas[0]) + pd.to_timedelta([1,2,3], unit='day')
                    else:
                        bd_pds_temp['fecha'] = pd.to_datetime(bd.fechas)

                    if símismo.datos_reg is None:
                        símismo.datos_reg = bd_pds_temp
                    else:
                        símismo.datos_reg.append(bd_pds_temp, ignore_index=True)

        # Generar datos regionales derivados de datos individuales
        símismo._gen_datos_reg()

    def _gen_datos_reg(símismo):

        datos_reg = símismo.datos_reg
        datos_ind = símismo.datos_ind

        nuevos = {v: [] for v in símismo.ind_a_reg}

        for v, d_v in símismo.ind_a_reg.items():

            combin = d_v['combin']
            if combin == 'prom':
                datos = datos_ind.groupby(['fecha', 'lugar']).mean()
            elif combin == 'suma':
                datos = datos_ind.groupby(['fecha', 'lugar']).sum()
            else:
                raise ValueError

            for i in datos.index:
                nuevos[v].append(datos.loc[i])
                nuevos['bd'].append('auto_gen')
                nuevos['fecha'].append(i[0])
                nuevos['lugar'].append(i[1])

        datos_reg.append(nuevos, ignore_index=True)

    def obt_datos(símismo, l_vars, lugar=None, cód_lugar=None, datos=None, fechas=None, escala=None):

        # Formatear la lista de variables deseados
        if not isinstance(l_vars, list):
            l_vars = [l_vars]
        if any(v not in símismo.vars for v in l_vars):
            raise ValueError(_('Variable no válido.'))

        # Formatear el código de lugar
        if cód_lugar is not None and not isinstance(cód_lugar, list):
                cód_lugar = [cód_lugar]

        # Obtener código de lugar, si necesario
        if lugar is not None:
            # para hacer
            if not isinstance(lugar, list):
                lugar = [lugar]

            if cód_lugar is None:

                cód_lugar = []
                for l in lugar:
                    dic = símismo.geog.árbol
                    dif = len(símismo.geog.orden_esc_geog) - len(l)
                    l += [''] * dif

                    for k in l:
                        dic = dic[k]

                    cód_lugar.append(dic)

            else:
                avisar(_('Lugar y código de lugar ambos especificados. Tomaremos el código.'))

        # Formatear los datos
        if datos is not None and not isinstance(datos, list):
            datos = [datos]

        # Preparar las fechas
        if fechas is not None:
            if not isinstance(fechas, list):
                fechas = [fechas]
            for í, f in enumerate(fechas):
                if isinstance(f, ft.date) or isinstance(f, ft.datetime):
                    pass
                elif isinstance(f, int):
                    fechas[í] = ft.date(year=f, month=1, day=1)

        egr = [None, None]
        for í, bd in enumerate([símismo.datos_reg, símismo.datos_ind]):
            l_vars_disp = [v for v in l_vars if v in bd]
            bd_sel = bd[l_vars_disp]

            if datos is not None:
                bd_sel = bd_sel[bd_sel['bd'].isin(datos)]

            if fechas is not None:
                bd_sel = bd_sel[bd_sel['fecha'].isin(fechas)]

            if cód_lugar is not None:
                bd_sel = bd_sel[bd_sel['lugar'].isin(cód_lugar)]

            egr[í] = bd_sel

        return {'regional': egr[0], 'individual': egr[1]}

    def graficar(símismo, var, fechas=None, cód_lugar=None, lugar=None, datos=None, escala=None):

        dic_datos = símismo.obt_datos(l_vars=var, fechas=fechas, cód_lugar=cód_lugar, lugar=lugar, datos=datos,
                                      escala=escala)

        if escala.lower()=='individual':
            d_ind = dic_datos['individual']

        else:
            d_reg = dic_datos['regional']
            n_fechas = d_reg['fecha'].nunique()
            n_lugares = d_reg['lugar'].nunique()

            if n_fechas > 1:
                pass


class _dinausorio(object):
    """
    En caso que haya algo interesante aquí.
    """

    def __init__(símismo, datos, geog=None, fuente=None):
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



    def graficar(símismo, var, escala='individual', años=None, cód_lugar=None, lugar=None, datos=None):

        dic_datos = símismo.pedir_datos(l_vars=[var], escala=escala, años=años,
                                        cód_lugar=cód_lugar, lugar=lugar, datos=datos)

        # El número máximo de años que tenga un lugares
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
        :type datos: Datos | list[Datos]

        :return:
        :rtype: dict

        """

        if escala not in (símismo.geog.órden + ['individual']):
            raise ValueError

        if cód_lugar is not None and lugar is not None:
            raise ValueError('No se puede especificar y un código de lugares, y el lugares. Hay que usar o el uno,'
                             'o el otro para identificar el lugares.')

        # Convertir una ubicación de lugares (lista) a código de lugares
        if lugar is not None:
            dic = símismo.geog.árbol
            dif = len(símismo.geog.órden) - len(lugar)
            lugar += [''] * dif

            for l in lugar:
                dic = dic[l]

            cód_lugar = dic

        if not isinstance(cód_lugar, list):
            cód_lugar = [cód_lugar]

        if datos is None:
            datos = símismo.datos

        if not isinstance(datos, list):
            datos = [datos]

        if escala == 'individual':
            lugares = símismo.geog.obt_lugares_en(cód_lugar=cód_lugar, escala=None)
        else:
            lugares = símismo.geog.obt_lugares_en(cód_lugar=cód_lugar, escala=escala)

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
            elif isinstance(v, dict):
                símismo.combinar_dics(d1=d1[ll], d2=v)
            elif isinstance(v, np.ndarray):
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

        with open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

    def cargar(símismo, fuente):

        with open(fuente, 'r', encoding='utf8') as d:
            nuevo_dic = json.load(d)

        símismo.receta.clear()
        símismo.receta.update(nuevo_dic)

        símismo.fuente = fuente


def _gen_bd(archivo):
    """

    :param archivo:
    :type archivo: str
    :return:
    :rtype: BD
    """
    ext = os.path.splitext(archivo)[1]
    if ext == '.txt' or ext == '.csv':
        return BDtexto(archivo)
    elif ext == '.sql':
        return BDsql(archivo)
    else:
        raise ValueError


class BD(object):
    """
    Una superclase para lectores de bases de datos.
    """

    def __init__(símismo, archivo):
        símismo.archivo = archivo

        if not os.path.isfile(archivo):
            raise FileNotFoundError

        símismo.n_obs = símismo.calc_n_obs()

    def obt_nombres_cols(símismo):
        """

        :return:
        :rtype: list[str]
        """
        raise NotImplementedError

    def obt_datos(símismo, cols, prec_dec=None):
        """

        :param cols:
        :type cols: list[str] | str
        :param prec_dec:
        :type prec_dec: int
        :return:
        :rtype: np.ndarray
        """
        raise NotImplementedError

    def obt_datos_tx(símismo, cols):
        """

        :param cols:
        :type cols: list[str] | str
        :return:
        :rtype: list
        """
        raise NotImplementedError

    def obt_fechas(símismo, cols):
        """

        :param cols:
        :type cols: str
        :return:
        :rtype: (ft.date, np.ndarray)
        """

        # Sacar la lista de fechas en formato texto
        fechas_tx = símismo.obt_datos_tx(cols=cols)

        # Procesar la lista de fechas
        fch_inic_datos, v_núm = símismo._leer_fechas(lista_fechas=fechas_tx)

        # Devolver información importante
        return fch_inic_datos, v_núm

    def calc_n_obs(símismo):
        """

        :return:
        :rtype: int
        """
        raise NotImplementedError

    @staticmethod
    def _leer_fechas(lista_fechas):
        """
        Esta función toma una lista de datos de fecha en formato de texto y detecta 1) la primera fecha de la lista,
        y 2) la posición relativa de cada fecha a esta.

        :param lista_fechas: Una lista con las fechas en formato de texto
        :type lista_fechas: list

        :return: Un tuple de la primera fecha y del vector numpy de la posición de cada fecha relativa a la primera.
        :rtype: (ft.date, np.ndarray)

        """

        # Una lista de lso formatos de fecha posibles. Esta función intentará de leer los datos de fechas con cada
        # formato en esta lista y, si encuentra un que funciona, parará allí.
        separadores = ['-', '/', ' ', '.']

        f = ['%d{0}%m{0}%y', '%m{0}%d{0}%y', '%d{0}%m{0}%Y', '%m{0}%d{0}%Y',
             '%d{0}%b{0}%y', '%m{0}%b{0}%y', '%d{0}%b{0}%Y', '%b{0}%d{0}%Y',
             '%d{0}%B{0}%y', '%m{0}%B{0}%y', '%d{0}%B{0}%Y', '%m{0}%B{0}%Y',
             '%y{0}%m{0}%d', '%y{0}%d{0}%m', '%Y{0}%m{0}%d', '%Y{0}%d{0}%m',
             '%y{0}%b{0}%d', '%y{0}%d{0}%b', '%Y{0}%b{0}%d', '%Y{0}%d{0}%b',
             '%y{0}%B{0}%d', '%y{0}%d{0}%B', '%Y{0}%B{0}%d', '%Y{0}%d{0}%B']

        formatos_posibles = [x.format(s) for s in separadores for x in f]

        # Primero, si los datos de fechas están en formato simplemente numérico...
        if all([x.isdigit() for x in lista_fechas]):

            # Entonces, no conocemos la fecha inicial
            fecha_inic_datos = None

            # Convertir a vector Numpy
            vec_fch_núm = np.array(lista_fechas, dtype=int)

        else:
            # Sino, intentar de leer el formato de fecha
            fechas = None

            # Intentar con cada formato en la lista de formatos posibles
            for formato in formatos_posibles:

                try:
                    # Intentar de convertir todas las fechas a objetos ft.datetime
                    fechas = [ft.datetime.strptime(x, formato).date() for x in lista_fechas]

                    # Si funcionó, parar aquí
                    break

                except ValueError:
                    # Si no funcionó, intentar el próximo formato
                    continue

            # Si todavía no lo hemos logrado, tenemos un problema.
            if fechas is None:
                raise ValueError(
                    'No puedo leer los datos de fechas. ¿Mejor le eches un vistazo a tu base de datos?')

            else:
                # Pero si está bien, ya tenemos que encontrar la primera fecha y calcular la posición relativa de las
                # otras con referencia en esta.

                # La primera fecha de la base de datos. Este paso se queda un poco lento, así que para largas bases de
                # datos podría ser útil suponer que la primera fila también contiene la primera fecha.
                fecha_inic_datos = min(fechas)

                # Si tenemos prisa, mejor lo hagamos así:
                # fecha_inic_datos = min(fechas[0], fechas[-1])

                # La posición relativa de todas las fechas a esta
                lista_fechas = [(x - fecha_inic_datos).days for x in fechas]

                # Convertir a vector Numpy
                vec_fch_núm = np.array(lista_fechas, dtype=int)

        return fecha_inic_datos, vec_fch_núm


class BDtexto(BD):
    """
    Una clase para leer bases de datos en formato texto delimitado por comas (.csv).
    """

    def calc_n_obs(símismo):
        """

        :rtype: int
        """
        with open(símismo.archivo) as d:
            n_filas = sum(1 for f in d if len(f)) - 1  # Sustrayemos la primera fila

        return n_filas

    def obt_datos(símismo, cols, prec_dec=None):
        """

        :param cols:
        :type cols: str | list[str]
        :param prec_dec:
        :type prec_dec: int
        :return:
        :rtype: np.ndarray
        """
        if not isinstance(cols, list):
            cols = [cols]

        m_datos = np.empty((len(cols), símismo.n_obs))

        with open(símismo.archivo, encoding='UTF8') as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                m_datos[:, n_f] = [tx_a_núm(f[c]) if f[c] != '' else np.nan for c in cols]

        if len(cols) == 1:
            m_datos = m_datos[0]

        if prec_dec is not None:
            if prec_dec == 0:
                m_datos = m_datos.astype(int)
            else:
                m_datos.round(prec_dec, out=m_datos)

        return m_datos

    def obt_datos_tx(símismo, cols):
        """

        :param cols:
        :type cols: list[str] | str
        :return:
        :rtype: list
        """
        if not isinstance(cols, list):
            cols = [cols]

        l_datos = [[''] * símismo.n_obs] * len(cols)

        with open(símismo.archivo) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                for i_c, c in enumerate(cols):
                    l_datos[i_c][n_f] = f[c]

        if len(cols) == 1:
            l_datos = l_datos[0]

        return l_datos

    def obt_nombres_cols(símismo):
        """

        :return:
        :rtype: list[str]
        """

        with open(símismo.archivo) as d:
            lector = csv.reader(d)

            nombres_cols = next(lector)

        return nombres_cols


class BDsql(BD):
    """
    Una clase para leer bases de datos en formato SQL.
    """

    def calc_n_obs(símismo):
        """

        :return:
        :rtype:
        """
        raise NotImplementedError

    def obt_datos(símismo, cols, prec_dec=None):
        """

        :param cols:
        :type cols:
        :param prec_dec:
        :type prec_dec:
        :return:
        :rtype:
        """
        raise NotImplementedError

    def obt_datos_tx(símismo, cols):
        """

        :param cols:
        :type cols:
        :return:
        :rtype:
        """
        raise NotImplementedError

    def obt_nombres_cols(símismo):
        """

        :return:
        :rtype:
        """
        raise NotImplementedError
