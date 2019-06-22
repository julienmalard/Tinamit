import datetime as ft
from warnings import warn as avisar

import numpy as np
import pandas as pd
import xarray as xr
from tinamit.config import _


class Datos(object):
    def __init__(símismo, nombre, fuente, tiempo=None, lugar=None, cód_vacío=None):
        """

        :param nombre:
        :type nombre: str

        :param fuente:
        :type fuente: str | pd.DataFrame | xr.Dataset | dict

        :param tiempo:
        :type tiempo: str | ft.date | ft.datetime | int


        :param lugar:
        :type lugar: str

        :param cód_vacío:
        :type cód_vacío: list[int | float | str] | int | float | str

        """

        símismo.nombre = nombre

        símismo.archivo_datos = fuente
        símismo.bd = _gen_bd(fuente, cód_vacío=cód_vacío)
        símismo.n_obs = símismo.bd.n_obs
        símismo.cols = símismo.bd.obt_nombres_cols()
        símismo.c_lugar = símismo.c_tiempo = None

        if lugar is None and 'lugar' in símismo.cols:
            lugar = 'lugar'
        if lugar is None:
            símismo.lugares = [lugar] * símismo.bd.n_obs
        elif lugar in símismo.cols:
            símismo.c_lugar = lugar
            símismo.lugares = símismo.bd.obt_datos_tx(col=lugar)
        else:
            símismo.lugares = [str(lugar).strip()] * símismo.bd.n_obs

        if tiempo is None:
            for c in ['tiempo', 'fecha']:
                if c in símismo.cols:
                    tiempo = c
                    break

        if tiempo is False:
            # noinspection PyTypeChecker
            tiempos = np.full(símismo.n_obs, np.datetime64('NaT'), dtype='datetime64')
        elif tiempo is None:
            tiempos = np.arange(símismo.n_obs)
        elif isinstance(tiempo, str):
            if tiempo in símismo.cols:
                símismo.c_tiempo = tiempo
                try:
                    tiempos = símismo.bd.obt_fechas(tiempo)
                except ValueError:
                    tiempos = símismo.bd.obt_datos(tiempo)[tiempo]

            else:
                try:
                    tiempos = pd.to_datetime([obt_fecha_ft(tiempo)] * símismo.n_obs)
                except ValueError:
                    raise ValueError(_('El valor "{}" para fechas no corresponde a una fecha reconocida o al nombre de '
                                       'una columna en la base de datos').format(tiempo))
        elif isinstance(tiempo, (ft.date, ft.datetime)):
            tiempos = pd.to_datetime([tiempo] * símismo.n_obs)
        elif isinstance(tiempo, int):
            tiempos = [tiempo] * símismo.n_obs
        else:
            raise TypeError(_('La fecha debe ser en formato texto, una fecha, o un número de año.'))

        símismo.tiempos = tiempos

        if cód_vacío is None:
            símismo.cód_vacío = {'', 'NA', 'na', 'Na', 'nan', 'NaN'}
        else:
            if isinstance(cód_vacío, (set, list)):
                símismo.cód_vacío = set(cód_vacío)
            else:
                símismo.cód_vacío = {cód_vacío}

            símismo.cód_vacío.add('')

    def obt_datos(símismo, l_vars):
        """

        :param l_vars:
        :type l_vars: list[str] | str

        :return:
        :rtype: pd.DataFrame

        """

        # Obtener los datos en formato Pandas
        datos = símismo.bd.obt_datos(l_vars)

        # Agregar una columna con el nombre de la base de datos y el lugar o lugares de observación
        bd = xr.Dataset({
            x: ('n', v) if len(v.shape) == 1 else (('n', *tuple('x' + str(i) for i in range(v.shape[1:]))), v)
            for x, v in datos.items()
        })
        bd.coords['bd'] = ('n', [símismo.nombre] * símismo.bd.n_obs)
        bd.coords['lugar'] = ('n', símismo.lugares)

        # Agregar la fecha de observación
        bd.coords['tiempo'] = ('n', símismo.tiempos)

        return bd


class SuperBD(object):
    """
    Una :class:`SuperBD` reune varias bases de :class:`Datos` en un lugar cómodo para acceder a los datos.
    """

    def obt_datos(símismo, l_vars=None, lugares=None, bd_datos=None, tiempos=None, excl_faltan=False,
                  tipo=None, interpolar=True, interpolar_estricto=False):
        """

        Parameters
        ----------
        l_vars: str | list[str]
        lugares: str | set[str] | list[str]
        bd_datos: str | Datos | list[str | Datos]
        tiempos: ft.date | ft.datetime | int | str | list | tuple
        excl_faltan: bool
        tipo: str
        interpolar: bool
        interpolar_estricto: bool

        Returns
        -------

        """

        # Seleccionar las observaciones que corresponden al lugar de interés
        if lugares is not None:
            bd_sel = bd_sel.where(bd_sel['lugar'].isin(list(lugares)), drop=True)

        # Interpolar si necesario
        if interpolar:
            bd_sel = símismo._interpolar(
                bd_sel, tiempos,
                interpol_en='lugar' if tipo != 'microdatos' else None,
                estricto=interpolar_estricto
            )

        # Seleccionar las observaciones en las fechas de interés
        if tiempos is not None:
            bd_sel = símismo._filtrar_tiempo(bd_sel, tiempos)

        # Si tenemos datos generales, tomamos promedios
        if tipo == 'datos':
            bd_sel = bd_sel.set_index(n=['lugar', 'tiempo']).groupby('n').mean().reset_index('n')
            if 'tiempo' not in bd_sel.coords:  # para hacer: algo más elegante
                bd_sel = bd_sel.rename({'n_level_0': 'lugar', 'n_level_1': 'tiempo'})

        # Excluir las observaciones que faltan
        if excl_faltan:
            # Si excluyemos las observaciones que faltan, guardar únicamente las filas con observacienes
            # para todos los variables
            bd_sel_final = bd_sel.dropna('n', subset=[x for x in bd_sel.data_vars])
            if len(bd_sel_final['tiempo'].values):
                bd_sel = bd_sel_final
            else:
                avisar('Extrapolando por falta de datos en variables: {}'.format(', '.join(l_vars)))
                bd_sel = bd_sel.dropna(
                    'n', subset=[x for x in bd_sel.data_vars]
                )
                for i, (l, f) in enumerate(zip(bd_sel['lugar'].values, bd_sel['tiempo'].values)):
                    for v in bd_sel.data_vars:
                        if np.isnan(bd_sel[v][i].values):
                            l_f = bd_sel['tiempo'].where(bd_sel['lugar'] == l).where(np.isfinite(bd_sel[v])).dropna(
                                'n').values
                            if not len(l_f):
                                continue
                            próx = l_f[np.abs(l_f - f).argmin()]
                            bd_sel[v].values[i] = np.mean(
                                bd_sel[v].where(bd_sel['lugar'] == l).where(bd_sel['tiempo'] == próx).dropna(
                                    'n').values)

                bd_sel = bd_sel.dropna('n', subset=[x for x in bd_sel.data_vars])

        else:
            # Sino, exlcuir únicamente las filas que faltans observaciones para todos los variables
            bd_sel = bd_sel.dropna(
                'n', subset=[x for x in bd_sel.data_vars], how='all'
            )

        return bd_sel

    @staticmethod
    def _interpolar(bd, fechas, interpol_en, estricto=False):
        """
        Efectua interpolaciones temporales.

        Parameters
        ----------
        bd : pd.DataFrame
            La base de datos en la cual interpolar.
        fechas :
        interpol_en: str
            La columna de categoría (por ejemplo, el lugar) con la cual hay que interpolar.
        estricto: bool
            Si enforzamos interpolaciones estríctas (únicamente las con datos disponibles a ambos lados de las fechas
            de interés), o si simplemente hacemos lo mejor posible sin preocuparse demasiado.

        Returns
        -------
        xr.Dataset
            Una nueva base de datos, únicamente con las fechas interpoladas.
        """

        # Si no estamos interpolando, paramos aquí.
        if interpol_en is None:
            return bd
        if bd['tiempo'].isnull().all():
            return bd
        # Asegurarse que la columna de categorías para la interpolacion existe.
        if interpol_en not in bd:
            raise ValueError(_('El variable "{}" no existe en esta base de datos.').format(interpol_en))

        # Categorías únicas en las cuales interpolar (por ejemplo, interpolar para cada lugar).
        categs_únicas = set(bd[interpol_en].values.tolist())

        # Preparar las fechas de interés.
        if fechas is None:
            fechas_interés = []  # Utilizar únicamente las fechas ya en la base de datos
        elif isinstance(fechas, tuple):
            fechas_interés = None  # En caso de rango, se calculará por cada categoría de interpolación
        elif isinstance(fechas, list):
            fechas_interés = fechas  # Una lista de fechas
        else:
            fechas_interés = [fechas]  # Asegurar que sea lista

        # ¡Ahora, calcular las interpolaciones!

        finalizados = None

        # Para cada categoría...
        for c in categs_únicas:

            # Tomar únicamente las filas que corresponden con la categoría actual.
            if c is None:
                bd_categ = bd.where(bd[interpol_en].isnull(), drop=True)
            else:
                bd_categ = bd.where(bd[interpol_en] == c, drop=True)

            # Calcular las fechas de interés para esta categoría, si necesario
            if fechas_interés is not None:
                f_interés_categ = fechas_interés
            else:
                # Tomar las fechas de esta categoría que están en el rango
                f_interés_categ = list(set([f.values for f in bd_categ['tiempo'] if fechas[0] <= f <= fechas[1]]))

            # Las nuevas fechas de interés que hay que a la base de datos
            nuevas_fechas = [x for x in f_interés_categ if not (bd_categ['tiempo'] == x).any()]

            # Agregar las nuevas fechas si necesario.
            if len(nuevas_fechas):
                # Crear una base de datos
                nuevas_filas = xr.Dataset(
                    data_vars={x: ('n', [np.nan] * len(nuevas_fechas))
                               for x in bd_categ.data_vars if x not in ['bd', 'tiempo', interpol_en]
                               },
                    coords=dict(tiempo=('n', nuevas_fechas),
                                bd=('n', ['interpolado'] * len(nuevas_fechas)),
                                **{interpol_en: ('n', [c] * len(nuevas_fechas))}
                                )
                )

                # ...y agregarla a la base de datos de la categoría actual.
                bd_categ = xr.concat([nuevas_filas, bd_categ], 'n')

            # Calcular el promedio de los valores de observaciones por categoría y por fecha
            proms_fecha = bd_categ.groupby('tiempo').mean()  # type: xr.Dataset
            n_obs = len(proms_fecha['tiempo'])
            bd_temp = xr.Dataset({v: ('n', proms_fecha[v]) for v in list(proms_fecha.variables)})
            bd_temp[interpol_en] = ('n', [c] * n_obs)
            bd_temp['bd'] = ('n', ['interpolado'] * n_obs)
            bd_temp.set_coords(['bd', 'tiempo', interpol_en], inplace=True)

            # Interpolar únicamente si quedan valores que faltan para las fechas de interés
            faltan = any(
                np.isnan(proms_fecha.where(proms_fecha['tiempo'].isin(f_interés_categ), drop=True)[x].values).any() for
                x
                in proms_fecha.data_vars)
            if faltan:

                # Aplicar valores para variables sin fechas asociadas (por ejemplo, tamaños de municipio)
                sin_fecha = bd.where(bd['tiempo'].isnull(), drop=True)
                if len(sin_fecha['n']) > 0:
                    proms_sin_fecha = sin_fecha.loc[sin_fecha[categs_únicas] == c].mean().to_frame().T
                    bd_temp = bd_temp.fillna(
                        value={ll: v[0] for ll, v in proms_sin_fecha.to_dict(orient='list').items()}
                    )

                # Por fin, interpolar
                bd_temp = bd_temp.interpolate_na('n', use_coordinate='tiempo')

                # Si quedaron combinaciones de variables y de fechas para las cuales no pudimos interpolar porque
                # las fechas que faltaban se encontraban afuera de los límites de los datos disponibles,
                # simplemente copiar el último valor disponible (y avisar).
                todavía_faltan = [x for x in bd_temp.data_vars if bd_temp.isnull().any()[x]]
                if len(todavía_faltan) and not estricto:
                    avisar(_('No pudimos interpolar de manera segura para todos los variables. Tomaremos los '
                             'valores más cercanos posibles.\nVariables problemáticos: "{}"')
                           .format(', '.join(todavía_faltan)))
                    for v in todavía_faltan:
                        existen = np.where(bd_temp[v].notnull())[0]
                        if len(existen):
                            primero = existen[0]
                            último = existen[-1]
                            bd_temp[v][:primero] = bd_temp[v][primero]
                            bd_temp[v][último + 1:] = bd_temp[v][último]

            # Agregar a los resultados finales
            if finalizados is None:
                finalizados = bd_temp
            else:
                finalizados = xr.concat([finalizados, bd_temp], 'n')
        return finalizados
