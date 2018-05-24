import csv
import datetime as ft
import json
import os
from warnings import warn as avisar

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura

from tinamit import _
from tinamit.Análisis.Números import tx_a_núm
from tinamit.Geog.Geog import Geografía


class Datos(object):
    def __init__(símismo, nombre, archivo, fecha=None, lugar=None, cód_vacío=None):
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

        if fecha is None:
            símismo.fechas = fecha
        elif fecha in símismo.cols:
            símismo.fechas = símismo.bd.obt_fechas(fecha)
        elif isinstance(fecha, ft.date) or isinstance(fecha, ft.datetime):
            símismo.fechas = fecha
        elif isinstance(fecha, int):
            símismo.fechas = ft.date(year=fecha, month=1, day=1)
        else:
            raise ValueError(_('El valor "{}" para fechas no corresponde a una fecha reconocida o al nombre de'
                               'una columna en la base de datos').format(fecha))

        if lugar is None:
            símismo.lugares = lugar
        elif lugar in símismo.cols:
            # Quitar 0's inútiles en frente del código.
            símismo.lugares = [x.strip().lstrip('0') for x in símismo.bd.obt_datos_tx(cols=lugar)]
        else:
            símismo.lugares = str(lugar).strip().lstrip('0')

        if cód_vacío is None:
            símismo.cód_vacío = {'', 'NA', 'na', 'Na', 'nan', 'NaN'}
        else:
            if isinstance(cód_vacío, set):
                símismo.cód_vacío = cód_vacío
            elif isinstance(cód_vacío, list):
                símismo.cód_vacío = set(cód_vacío)
            else:
                símismo.cód_vacío = {cód_vacío}

            símismo.cód_vacío.add('')

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

        códs_vacío_final = símismo.cód_vacío.copy()
        if cód_vacío is not None:
            if isinstance(cód_vacío, list) or isinstance(cód_vacío, set):
                códs_vacío_final.update(cód_vacío)
            else:
                códs_vacío_final.add(cód_vacío)

        datos = símismo.bd.obt_datos(l_vars, cód_vacío=códs_vacío_final)

        return datos

    def __str__(símismo):
        return símismo.nombre


class DatosIndividuales(Datos):
    """
    No tiene funcionalidad específica, pero esta clase queda muy útil para identificar el tipo de datos.
    """

    def __init__(símismo, nombre, archivo, fecha, lugar, cód_vacío=None):
        super().__init__(nombre=nombre, archivo=archivo, fecha=fecha, lugar=lugar, cód_vacío=cód_vacío)


class DatosRegión(Datos):

    def __init__(símismo, nombre, archivo, fecha=None, lugar=None, cód_vacío=None, tmñ_muestra=None):

        super().__init__(nombre=nombre, archivo=archivo, fecha=fecha, lugar=lugar, cód_vacío=cód_vacío)

        símismo.tmñ_muestra = tmñ_muestra
        if tmñ_muestra is not None:
            if tmñ_muestra not in símismo.cols:
                raise ValueError(_('Nombre de columna de tamaños de muestra "{}" erróneo.').format(tmñ_muestra))

    def obt_error(símismo, var, col_error=None):

        errores = None
        if col_error is not None:
            errores = símismo.bd.obt_datos(col_error)
        else:
            datos = símismo.bd.obt_datos(var, cód_vacío=símismo.cód_vacío)
            if símismo.tmñ_muestra is not None:
                if np.nanmin(datos) >= 0 and np.nanmax(datos) <= 1:
                    tmñ_muestra = símismo.bd.obt_datos(símismo.tmñ_muestra, cód_vacío=símismo.cód_vacío)
                    errores = np.sqrt(np.divide(np.multiply(datos, np.subtract(1, datos)), tmñ_muestra))
            else:
                errores = np.empty_like(datos)
                errores[:] = np.nan

        return errores


class SuperBD(object):

    def __init__(símismo, nombre, bds=None, geog=None):
        """

        :param nombre:
        :type nombre: str
        :param bds:
        :type bds: list | Datos
        :param geog:
        :type geog: Geografía
        """

        símismo.nombre = nombre
        símismo.geog = geog

        if bds is None:
            símismo.bds = {}  # type: dict[Datos]
        else:
            if isinstance(bds, Datos):
                bds = [bds]
            if isinstance(bds, list):
                símismo.bds = {d.nombre: d for d in bds}  # type: dict[str, Datos]
            else:
                raise TypeError('')

        símismo.vars = {}
        símismo.receta = {'vars': símismo.vars, 'bds': []}

        símismo.datos_reg = None  # type: pd.DataFrame
        símismo.datos_reg_err = None  # type: pd.DataFrame
        símismo.datos_ind = None  # type: pd.DataFrame
        símismo.bd_lista = False

    def agregar_datos(símismo, bd, bd_plantilla=None, auto_llenar=True):
        """

        :param bd:
        :type bd: Datos
        :param bd_plantilla:
        :type bd_plantilla: str | list[str] | Datos
        :param auto_llenar:
        :type auto_llenar: bool

        """

        if bd in símismo.bds:
            avisar(_('Ya existía la base de datos "{}". Borramos la que estaba antes.').format(bd))

        símismo.bds[bd.nombre] = bd
        #  símismo.receta['bds'].append(bd.archivo_datos)

        if auto_llenar:
            símismo.auto_llenar(bd=bd, bd_plantilla=bd_plantilla)

        símismo.bd_lista = False

    def auto_llenar(símismo, bd, bd_plantilla):
        if bd_plantilla is None:
            bd_plantilla = [x for x in símismo.bds if x != bd]
        if not isinstance(bd_plantilla, list):
            bd_plantilla = [bd_plantilla]

        for var, d_var in símismo.vars.items():
            for b in d_var['fuente']:
                if b in bd_plantilla:
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

        símismo.bd_lista = False

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

        símismo.bd_lista = False

    def espec_var(símismo, var, var_bd=None, bds=None, cód_vacío='', var_err=None):

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

        for nm_bd in bds.copy():

            if var_bd not in símismo.bds[nm_bd].cols:
                avisar(_('"{}" no existe en base de datos "{}".').format(var_bd, nm_bd))
                bds.remove(nm_bd)

        if not len(bds):
            raise ValueError('El variable "{}" no existe en cualquiera de las bases de datos especificadas.'
                             .format(var_bd))

        if var not in símismo.vars:
            símismo.vars[var] = {'fuente': {bd: {'var': var_bd, 'cód_vacío': cód_vacío} for bd in bds}}
        else:
            for bd in bds:
                símismo.vars[var]['fuente'][bd] = {'var': var_bd, 'cód_vacío': cód_vacío}

        # Agregar información de error para bases de datos regionales
        for bd in bds:
            if isinstance(símismo.bds[bd], DatosRegión):
                símismo.vars[var]['fuente'][bd]['col_error'] = var_err

        símismo.bd_lista = False

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

        símismo.bd_lista = False

    def renombrar_var(símismo, var, nuevo_nombre):

        if var not in símismo.vars:
            raise ValueError('')
        if nuevo_nombre in símismo.vars:
            raise ValueError(_('El variable "{}" ya existe. Hay que borrarlo primero.').format(nuevo_nombre))

        símismo.vars[nuevo_nombre] = símismo.vars.pop(var)

        símismo.bd_lista = False

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
            if bd_pd is not None:
                cols = list(bd_pd)
                for c in cols:
                    if c not in list(símismo.vars) + ['bd', 'lugar', 'fecha']:
                        bd_pd.drop(c, axis=1, inplace=True)

        # Quitar observaciones en bases de datos que ya no están vinculadas
        if símismo.datos_ind is not None:
            símismo.datos_ind = datos_ind[datos_ind['bd'].isin(símismo.bds)]
        if símismo.datos_reg is not None:
            símismo.datos_reg = datos_reg[datos_reg['bd'].isin(símismo.bds)]

    def _gen_bd_intern(símismo):

        símismo._limp_vars()
        símismo.datos_ind = símismo.datos_reg = None

        # Agregar datos
        for nb, bd in símismo.bds.items():

            vars_interés = [it for it in símismo.vars.items() if nb in it[1]['fuente']]
            l_vars = [it[0] for it in vars_interés]

            if len(vars_interés):
                l_vars_bd = [d_v['fuente'][nb]['var'] for _, d_v in vars_interés]
                l_códs_vac = [d_v['fuente'][nb]['cód_vacío'] for _, d_v in vars_interés]

                datos_bd = np.array(bd.obt_datos(l_vars=l_vars_bd, cód_vacío=l_códs_vac)).T

                bd_pds_temp = pd.DataFrame(datos_bd, columns=l_vars)

                bd_pds_temp['bd'] = nb
                bd_pds_temp['lugar'] = bd.lugares

                if isinstance(bd.fechas, tuple):
                    if bd.fechas[0] is not None:
                        bd_pds_temp['fecha'] = pd.to_datetime(bd.fechas[0]) + pd.to_timedelta(bd.fechas[1], unit='d')
                    else:
                        bd_pds_temp['fecha'] = pd.to_datetime(['{}-1-1'.format(str(x)) for x in bd.fechas[1]])
                elif bd.fechas is None:
                    bd_pds_temp['fecha'] = None
                else:
                    bd_pds_temp['fecha'] = pd.to_datetime(bd.fechas)

                # Datos individuales
                if isinstance(bd, DatosIndividuales):

                    if símismo.datos_ind is None:
                        símismo.datos_ind = bd_pds_temp
                    else:
                        símismo.datos_ind = pd.concat([bd_pds_temp, símismo.datos_ind], ignore_index=True)

                # Datos regionales
                else:

                    if símismo.datos_reg is None:
                        símismo.datos_reg = bd_pds_temp
                    else:
                        símismo.datos_reg = pd.concat([bd_pds_temp, símismo.datos_reg], ignore_index=True)

                    # Calcular errores
                    datos_err = np.array(
                        [bd.obt_error(d_v['fuente'][nb]['var'], col_error=d_v['fuente'][nb]['col_error'])
                         for v, d_v in vars_interés]
                    ).T
                    bd_pds_err_temp = bd_pds_temp.copy()
                    bd_pds_err_temp[l_vars] = datos_err

                    if símismo.datos_reg_err is None:
                        símismo.datos_reg_err = bd_pds_temp
                    else:
                        símismo.datos_reg_err.append(bd_pds_temp, ignore_index=True)

        símismo.bd_lista = True

    def obt_datos(símismo, l_vars, lugar=None, datos=None, fechas=None, excl_faltan=False):

        # Formatear la lista de variables deseados
        if not isinstance(l_vars, list):
            l_vars = [l_vars]
        if any(v not in símismo.vars for v in l_vars):
            raise ValueError(_('Variable no válido.'))

        # Formatear el código de lugar
        if lugar is not None:
            if not isinstance(lugar, list):
                lugar = [lugar]

        # Formatear los datos
        if datos is not None:
            if not isinstance(datos, list):
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

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        egr = [None, None, None]
        for í, bd in enumerate([símismo.datos_reg, símismo.datos_ind, símismo.datos_reg_err]):

            if bd is not None:
                l_vars_disp = [v for v in l_vars if v in bd]
                bd_sel = bd[l_vars_disp + ['bd', 'fecha', 'lugar']]

                if datos is not None:
                    bd_sel = bd_sel[bd_sel['bd'].isin(datos)]

                if fechas is not None:
                    bd_sel = bd_sel[bd_sel['fecha'].isin(fechas)]  # Arreglarme

                if lugar is not None:
                    bd_sel = bd_sel[bd_sel['lugar'].isin(lugar)]

                if excl_faltan:
                    bd_sel = bd_sel.dropna(subset=[x for x in bd_sel.columns if x not in ['fecha', 'bd', 'lugar']])
                else:
                    bd_sel = bd_sel.dropna(subset=[x for x in bd_sel.columns if x not in ['fecha', 'bd', 'lugar']],
                                           how='all')
                egr[í] = bd_sel

        return {'regional': egr[0], 'error_regional': egr[2], 'individual': egr[1]}

    def obt_datos_ind(símismo, l_vars, lugar=None, datos=None, fechas=None, excl_faltan=False):
        res = símismo.obt_datos(l_vars=l_vars, lugar=lugar, datos=datos, fechas=fechas, excl_faltan=excl_faltan)
        return res['individual']

    def obt_datos_reg(símismo, l_vars, lugar=None, datos=None, fechas=None, interpolar=True):
        res = símismo.obt_datos(l_vars=l_vars, lugar=lugar, datos=datos, fechas=fechas, excl_faltan=False)['regional']

        if interpolar:
            finalizados = None
            for l in lugar:
                proms_fecha = res.loc[res['lugar'] == l].groupby(['fecha']).mean()
                if proms_fecha.shape[0] > 0:

                    # Aplicar valores sin fechas asociadas
                    sin_fecha = res[res.fecha.isnull()]
                    if sin_fecha.shape[0] > 0:
                        proms_sin_fecha = sin_fecha.loc[sin_fecha['lugar'] == l].mean().to_frame().T
                        proms_fecha.fillna(value={ll: v[0] for ll, v in proms_sin_fecha.to_dict(orient='list').items()},
                                           inplace=True)

                    mín = proms_fecha.index.min()
                    máx = proms_fecha.index.max()

                    for v in l_vars:
                        compl_v = proms_fecha.dropna(subset=[v])[v]
                        mín_v = compl_v.index.min()
                        máx_v = compl_v.index.max()
                        mín = max(mín, mín_v)
                        máx = min(máx, máx_v)

                    l_fechas_fin = [í for í in proms_fecha.index if mín <= í <= máx]

                    if len(l_fechas_fin):
                        nuevas_filas = pd.DataFrame(columns=l_vars,
                                                    index=pd.to_datetime(
                                                        [x for x in l_fechas_fin if x not in proms_fecha.index]))
                        proms_fecha = proms_fecha.append(nuevas_filas)
                        proms_fecha = proms_fecha.sort_index()
                        proms_fecha = proms_fecha.interpolate(method='time')
                        proms_fecha['lugar'] = l
                        proms_fecha = proms_fecha.loc[l_fechas_fin]
                    else:
                        avisar('No se pudo interpolar entre datos "{}". Nos basaremos simplemente en los datos '
                               'observados sin tener cuenta de la fecha de observación.'.format(l_vars))
                        proms_fecha = proms_fecha.sort_index()
                        proms_fecha.interpolate(limit_direction='both', inplace=True)
                    if finalizados is None:
                        finalizados = proms_fecha.dropna(how='any')
                    else:
                        finalizados = finalizados.append(proms_fecha.dropna(how='any'))
            return finalizados
        else:
            return res

    def graficar(símismo, var, fechas=None, cód_lugar=None, lugar=None, datos=None, escala=None, archivo=None):

        dic_datos = símismo.obt_datos(l_vars=var, fechas=fechas, cód_lugar=cód_lugar, lugar=lugar, datos=datos,
                                      escala=escala)

        fig = Figura()
        TelaFigura(Figura)
        ejes = fig.add_subplot(111)
        ejes.set_aspect('equal')

        if escala.lower() == 'individual':
            d_ind = dic_datos['individual']
            fechas = d_ind['fecha'].unique()
            lugares = d_ind['lugar'].unique()

            for l in lugares:
                for f in fechas:
                    ejes.hist(d_ind[d_ind['lugar'] == l and d_ind['fecha'] == f][var], label='{}, {}'.format(l, f))

            ejes.set_xlabel(var)
            ejes.set_ylabel(_('Freq'))
            ejes.legend()

        else:
            d_reg = dic_datos['regional']
            d_err = dic_datos['error_regional']

            fechas = d_reg['fecha']
            n_fechas = len(fechas.unique())
            lugares = d_reg['lugar'].unique()
            n_lugares = len(lugares)

            if n_fechas > 1:
                for l in lugares:
                    y = d_reg[d_reg['lugar'] == l][var]
                    err = d_err[d_err['lugar'] == l][var]

                    l = ejes.plot_date(fechas, y, label=l)
                    color = l.get_color()
                    ejes.fill_between(fechas, y - err / 2, y + err / 2, facecolor=color, alpha=0.5)

                ejes.set_xlabel(_('Fecha'))
                ejes.set_ylabel(var)
                ejes.legend()

            else:
                ejes.bar(n_lugares, d_reg[var])
                ejes.set_ylabel(var)
                ejes.set_xlabel(_('Lugar'))
                ejes.set_xticks(range(n_lugares))
                ejes.set_xticklabels(lugares)

        ejes.set_title(var)
        fig.savefig()

    def graf_comparar(símismo, var_x, var_y, fechas=None, cód_lugar=None, lugar=None, datos=None, escala=None,
                      archivo=None):
        datos = símismo.obt_datos(l_vars=[var_x, var_y], lugar=lugar, cód_lugar=cód_lugar, datos=datos, fechas=fechas,
                                  escala=escala)

        fig = Figura()
        TelaFigura(Figura)
        ejes = fig.add_subplot(111)
        ejes.set_aspect('equal')

        if escala.lower() == 'individual':
            ejes.plot(datos['individual'][var_x], datos['individual'][var_y])

        else:
            ejes.plot(datos['regional'][var_x], datos['regional'][var_y])

        ejes.set_title(_('{} vs {}').format(var_x, var_y))
        fig.savefig()

    def guardar_datos(símismo, archivo=None):
        if archivo is None:
            raise NotImplementedError  # para hacer

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        dic = {'ind': símismo.datos_ind.to_json(), 'reg': símismo.datos_reg.to_json(),
               'err': símismo.datos_reg_err.to_json()}

        with open(archivo, encoding='UTF-8') as d:
            json.dump(dic, d, ensure_ascii=False)

    def cargar_datos(símismo, archivo=None):
        if archivo is None:
            raise NotImplementedError  # para hacer

        with open(archivo, encoding='UTF-8') as d:
            dic = json.load(d)

        símismo.datos_ind = pd.read_json(dic['ind'])
        símismo.datos_reg = pd.read_json(dic['reg'])
        símismo.datos_reg_err = pd.read_json(dic['err'])

    def exportar_datos(símismo, directorio=None):
        if directorio is None:
            raise NotImplementedError  # para hacer

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        for nmb, bd_pd in {'ind': símismo.datos_ind, 'reg': símismo.datos_reg, 'error_reg': símismo.datos_reg_err}:
            archivo = os.path.join(directorio, nmb + '.csv')
            bd_pd.to_csv(archivo)

    def guardar(símismo, archivo=None):
        if archivo is None:
            raise NotImplementedError  # Para hacer

        with open(archivo, encoding='UTF-8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)

    @classmethod
    def cargar(cls, archivo):

        with open(archivo, encoding='UTF-8') as d:
            receta = json.load(d)

        nombre = os.path.splitext(os.path.split(archivo)[1])[0]

        try:
            d_bds = receta['bds']  # Para hacer
            bds = [DatosRegión(**d) for d in d_bds['regionales']]
            bds.append += [DatosIndividuales(**d) for d in d_bds['individuales']]

        except KeyError:
            bds = None

        try:
            geog = Geografía(receta['geog'][0])
            geog.cargar(receta['geog'][1])  # Para hacer
        except KeyError:
            geog = None

        superbd = cls(nombre=nombre, bds=bds, geog=geog)
        superbd.vars = receta['vars']

        return superbd


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

    def obt_datos(símismo, cols, prec_dec=None, cód_vacío=None):
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
        :rtype: list[str]
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

    def obt_datos(símismo, cols, prec_dec=None, cód_vacío=None):
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

        if cód_vacío is None:
            cód_vacío = ['']
        elif not isinstance(cód_vacío, set):
            cód_vacío = set(cód_vacío)

        m_datos = np.empty((len(cols), símismo.n_obs))

        with open(símismo.archivo) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                m_datos[:, n_f] = [tx_a_núm(f[c]) if f[c] not in cód_vacío else np.nan for c in cols]

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
