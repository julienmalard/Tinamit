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


class MicroDatos(Datos):
    """
    No tiene funcionalidad específica, pero esta clase queda muy útil para identificar el tipo de datos.
    """

    def __init__(símismo, nombre, fuente, tiempo=None, lugar=None, cód_vacío=None):
        super().__init__(nombre=nombre, fuente=fuente, tiempo=tiempo, lugar=lugar, cód_vacío=cód_vacío)


class SuperBD(object):
    """
    Una :class:`SuperBD` reune varias bases de :class:`Datos` en un lugar cómodo para acceder a los datos.
    """

    @staticmethod
    def _validar_fechas(fechas):
        """

        Parameters
        ----------
        fechas: ft.date | ft.datetime | str | list | tuple
            Si es una fecha o una cadena de texto, se interpretará como una fecha única de interés. Si es una lista,
            se interpretará como una lista de fechas de interés. Si es una tupla, se interpretará como un **rango**
            de fechas de interés.

        Returns
        -------
        ft.date | ft.datetime | str | list | tuple | int:
            Las fechas validadas.

        """

        def verificar_fecha(fch):
            """
            Verifica un fecha.

            Parameters
            ----------
            fch : str | ft.date | ft.datetime | int
                La fecha para verificar.

            Returns
            -------
            str | ft.date | ft.datetime
                La fecha validada.

            Raises
            ------
            ValueError
                Si la fecha no es válida.

            """

            if isinstance(fch, (ft.date, ft.datetime)):
                pass
            elif fch is None:
                return fch
            elif isinstance(fch, (int, float, np.float, np.int)):
                return int(fch)

            elif isinstance(fch, str):
                if len(fch) == 7:
                    fch += '-01'
                elif len(fch) == 4:
                    fch += '-01-01'
                try:
                    fch = ft.datetime.strptime(fch, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(_('La fecha "{}" no está en el formato "AAAA-MM-DD"').format(fch))
            else:
                raise TypeError(_('Tipo de fecha "{}" no reconocido.').format(type(fch)))

            return np.datetime64(fch)

        if fechas is None:
            # Si tenemos nada, devolver nada
            pass
        elif isinstance(fechas, tuple):
            # El caso de un rango de fechas

            # Un rango debe tener 2 elementos, nada más, nada menos
            if len(fechas) != 2:
                raise ValueError(
                    _('Se especificas un rango de fechas, el tuple debe tener exactamente 2 elemento,'
                      'no "{}". Si quieres obtener datos para una serie de fechas, pasar un lista al'
                      'parámetro `fechas` en vez.').format(len(fechas))
                )

            # Verificar que las fechas sean válidas
            l_fechas = []
            for f in fechas:
                l_fechas.append(verificar_fecha(f))

            fechas = tuple(l_fechas)

        elif isinstance(fechas, list):
            # El caso de una lista de fechas de interés

            # Verificar que las fechas sean válidas
            for í in range(len(fechas)):
                fechas[í] = verificar_fecha(fechas[í])

        else:
            # Sino, tenemos una única fecha
            fechas = verificar_fecha(fechas)

        return fechas

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

        # Formatear la lista de variables deseados
        if l_vars is None:
            l_vars = list(símismo.variables)
        l_vars = símismo._validar_var(l_vars)
        if not isinstance(l_vars, list):
            l_vars = [l_vars]

        # Formatear el código de lugar
        if lugares is not None:
            if isinstance(lugares, (str, int)):
                lugares = {lugares}

        # Formatear los datos
        bd_datos = símismo._validar_bd(bd_datos)
        if bd_datos is not None and not isinstance(bd_datos, list):
            bd_datos = [bd_datos]

        # Preparar las fechas
        if tiempos is not None:
            tiempos = símismo._validar_fechas(tiempos)
            l_tiempos = tiempos if isinstance(tiempos, (list, tuple, set)) else [tiempos]
            if símismo.tiempo_fecha() is not all(isinstance(t, np.datetime64) for t in l_tiempos):
                raise ValueError(
                    _('Debes emplear fechas caléndricas con, y únicamente con, bases de datos caléndricos.')
                )

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        if tipo is None:
            bd = None
            for dt in [símismo.microdatos, símismo.datos]:
                if dt is not None and all(v in dt.data_vars for v in l_vars):
                    bd = dt
                    break
            if bd is None:
                raise ValueError(_('Los variables "{}" no corresponden con microdatos o con datos normales.')
                                 .format(', '.join(l_vars)))
        else:
            tipo = tipo.lower()  # Formatear tipo
            if tipo == 'microdatos':
                bd = símismo.microdatos
            elif tipo == 'datos':
                bd = símismo.datos
            elif tipo == 'error':
                bd = símismo.datos_err
            else:
                raise ValueError(_('`tipo` debe ser uno de "{}"').format('"microdatos", "datos", o "error".'))

        # Asegurarse que existe esta base de datos
        if bd is None:
            raise ValueError(_('No tenemos datos para la base de datos "{}".').format(tipo))

        # Seleccionar los variables de interés
        bd_sel = bd[l_vars + ['bd', 'tiempo', 'lugar']]

        # Seleccionar las observaciones que vienen de la base de datos subyacente de interés
        if bd_datos is not None:
            bd_sel = bd_sel.where(bd_sel['bd'].isin(list(bd_datos)), drop=True)

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


class BD(object):
    """
    Una superclase para lectores de bases de datos.
    """

    def obt_fechas(símismo, cols):
        """

        :param cols:
        :type cols: str
        :return:
        :rtype: (ft.date, np.ndarray)
        """

        # Sacar la lista de fechas en formato texto
        fechas_tx = símismo.obt_datos_tx(col=cols)

        # Procesar la lista de fechas
        return símismo._leer_fechas(lista_fechas=fechas_tx)

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

        # Primero, si los datos de fechas están en formato simplemente numérico...
        if all([x.isdigit() for x in lista_fechas]):

            # Entonces, no conocemos la fecha inicial
            fecha_inic_datos = None

            # Convertir a vector Numpy
            vec_fch_núm = np.array(lista_fechas, dtype=int)

        else:
            # Sino, intentar de leer el formato de fecha
            fechas = obt_fecha_ft(lista_fechas)

            # Ya tenemos que encontrar la primera fecha y calcular la posición relativa de las
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

        if fecha_inic_datos is not None:
            # Una fecha original y una secuencia de no. de días relativos a la fecha original
            return pd.to_datetime(fecha_inic_datos) + pd.to_timedelta(vec_fch_núm, unit='d')
        else:
            # Una lista de años
            return pd.to_datetime(['{}-1-1'.format(str(x)) for x in vec_fch_núm])


def obt_fecha_ft(fechas):
    """
    Intentará leer los datos de fechas con cada formato posible, y parará en el primero que funciona.

    Parameters
    ----------
    fechas : str | list[str] | int
        La o las fechas para analizar.

    Returns
    -------
    ft.date | list[ft.date]
        La fecha o lista de fechas correspondientes.

    """

    # Una lista de los formatos de fecha posibles.
    separadores = ['-', '/', ' ', '.']

    f = ['%d{0}%m{0}%y', '%m{0}%d{0}%y', '%d{0}%m{0}%Y', '%m{0}%d{0}%Y',
         '%d{0}%b{0}%y', '%m{0}%b{0}%y', '%d{0}%b{0}%Y', '%b{0}%d{0}%Y',
         '%d{0}%B{0}%y', '%m{0}%B{0}%y', '%d{0}%B{0}%Y', '%m{0}%B{0}%Y',
         '%y{0}%m{0}%d', '%y{0}%d{0}%m', '%Y{0}%m{0}%d', '%Y{0}%d{0}%m',
         '%y{0}%b{0}%d', '%y{0}%d{0}%b', '%Y{0}%b{0}%d', '%Y{0}%d{0}%b',
         '%y{0}%B{0}%d', '%y{0}%d{0}%B', '%Y{0}%B{0}%d', '%Y{0}%d{0}%B']

    formatos_posibles = [x.format(s) for s in separadores for x in f]

    if isinstance(fechas, (list, tuple, np.ndarray)):
        lista_fechas = fechas
    else:
        lista_fechas = [fechas]

    if all(isinstance(f, (ft.datetime, ft.date)) for f in lista_fechas):
        fechas_ft = lista_fechas
    else:
        try:
            # Interntar convertir números de años de una vez
            fechas_ft = [ft.date(year=int(f), month=1, day=1) for f in lista_fechas]
        except (ValueError, TypeError):

            # Intentar con cada formato en la lista de formatos posibles
            fechas_ft = None
            for formato in formatos_posibles:

                try:
                    # Intentar de convertir todas las fechas a objetos ft.datetime
                    fechas_ft = [ft.datetime.strptime(x, formato).date() for x in lista_fechas]

                    # Si funcionó, parar aquí
                    break

                except ValueError:
                    # Si no funcionó, intentar el próximo formato
                    continue

        # Si todavía no lo hemos logrado, tenemos un problema.
        if fechas_ft is None:
            raise ValueError(
                'No puedo leer los datos de fechas. ¿Mejor le eches un vistazos?'
                '\n"{}"'.format(', '.join(lista_fechas[:10])))

    if isinstance(fechas, (list, tuple, np.ndarray)):
        return fechas_ft
    else:
        return fechas_ft[0]
