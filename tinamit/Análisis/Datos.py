import csv
import datetime as ft
import os
from warnings import warn as avisar

import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura

from tinamit.Análisis.Números import tx_a_núm
from tinamit.config import _
from tinamit.cositas import detectar_codif, guardar_json, cargar_json


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

    def __str__(símismo):
        return símismo.nombre

    def __getitem__(símismo, itema):
        return símismo.bd.obt_datos(itema)

    def obt_error(símismo, var, col_error='+ES'):

        if col_error is None:
            col_error = '+ES'
        col_error_final = None
        if col_error.startswith('+'):
            suf_err = col_error.lstrip('+')
            for col in símismo.cols:
                if col.endswith(suf_err) and col.rstrip(suf_err) == var.strip():
                    col_error = col.rstrip(suf_err)
                    break
        else:
            if col_error in símismo.cols:
                col_error_final = col_error
        if col_error_final is not None:
            errores = símismo.bd.obt_datos(col_error)
        else:
            datos = símismo.bd.obt_datos(var)[var]
            errores = np.empty_like(datos)
            errores[:] = np.nan

        return errores


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

    def __init__(símismo, nombre, bds=None, auto_conectar=True):
        """

        Parameters
        ----------
        nombre: str
            El nombre de la base de datos.
        bds: list[Datos] | Datos
            Una lista opcional de bases de :class:`Datos` para conectar.

        """

        # Guardar el nombre
        símismo.nombre = nombre

        # Las bases de datos
        símismo.bds = {}  # type: dict[str, Datos]

        # Información de variables (y de sus bases de datos correspondientes)
        símismo.variables = {}

        # Bases de datos internas
        símismo.datos = None  # type: pd.DataFrame
        símismo.datos_err = None  # type: pd.DataFrame
        símismo.microdatos = None  # type: pd.DataFrame

        # Si nuesta base de datos interna está actualizada o no.
        símismo.bd_lista = False

        # Guardar las bases de datos
        if bds is not None:
            if isinstance(bds, Datos):
                bds = [bds]
            for bd in bds:
                símismo.conectar_datos(bd, auto_conectar=auto_conectar)

    def conectar_datos(símismo, bd, auto_conectar=True):
        """
        Agregar una base de datos.

        Parameters
        ----------
        bd: Datos
            Los datos para agregar.
        auto_conectar: bool
            Si conectamos las columnas de esta nueva base de datos automáticamente.

        """

        # Avisar si existía antes.
        if bd.nombre in símismo.bds:
            avisar(_('Ya existía la base de datos "{}". Borramos la que estaba antes.').format(bd))

        # Agregar la base de datos
        símismo.bds[bd.nombre] = bd

        # Conectar los variables automáticamente, si queremos
        if auto_conectar:
            for var in bd.cols:
                if var not in [bd.c_lugar, bd.c_tiempo]:
                    símismo.espec_var(var=var, bds=bd)

        # Nuestras bases de datos internas ya no están actualizadas
        símismo.bd_lista = False

    def conectar_como(símismo, bd, bd_plantilla=None):
        """
        Conecta los variables de una base de :class:`Datos` automáticamente.

        Parameters
        ----------
        bd: Datos | str
            La base de datos para conectar.
        bd_plantilla: Datos | str
            La base de datos existente para servir de plantilla. Si es ``None``, se emplearán
            todas las bases de datos ya conectadas.

        """

        # Si `bd_plantilla` es ``None``, utilizar todas las bases de datos
        if bd_plantilla is None:
            bd_plantilla = [x for x in símismo.bds if x != bd]

        # Convertir a lista si necesario
        if not isinstance(bd_plantilla, list):
            bd_plantilla = [bd_plantilla]

        # Y convertir a nombres de bd
        for í in range(len(bd_plantilla)):
            bd_plantilla[í] = símismo._validar_bd(bd_plantilla[í])

        # Hacer las conexiones.
        for var, d_var in símismo.variables.items():
            # Para cada variable ya conectado...
            for b in list(d_var['fuente']):
                # Para cada base de datos que sirve de fuente para este variable...

                if b in bd_plantilla:
                    # Si la base de datos cuenta como plantilla...

                    # Leer el nombre del variable en la base de datos original
                    var_bd = d_var['fuente'][b]['var']

                    # Si existe este variable en la nueva base de datos también, copiar la especificación.
                    if var_bd in bd.cols:
                        d_var['fuente'][bd.nombre] = {**d_var['fuente'][b]}

                        # Ya pasar al próximo variable
                        continue

                    else:
                        # Si no encontramos el variable en cualquier base de datos, avisarlo.
                        avisar(_('El variable existente "{}" no existe en la nueva base de datos "{}". No'
                                 'lo podremos copiar.').format(var_bd, bd.nombre))

        # Ya no está actualizada nuestra base de datos interna.
        símismo.bd_lista = False

    def desconectar_datos(símismo, bd):
        """
        Desconectar una base de datos.

        Parameters
        ----------
        bd: Datos | str
            La base de datos para desconectar.

        """

        # Validar el nombre de la base de datos.
        bd = símismo._validar_bd(bd)

        # Quitarla.
        símismo.bds.pop(bd)

        # Quitar la de todos los diccionarios de variables también.
        for var, d_var in símismo.variables.items():
            try:
                d_var['fuente'].pop(bd)
            except KeyError:
                pass

        # Nuestas bases de datos internas ya necesitan ser actualizadas.
        símismo.bd_lista = False

    def lugares(símismo, tipo='datos'):
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        if tipo == 'microdatos':
            bd = símismo.microdatos
        elif tipo == 'datos':
            bd = símismo.datos
        else:
            raise ValueError
        if bd is None:
            return set()
        return set(bd['lugar'].values)

    def tiempos(símismo, tipo='datos', lugar=None):
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        if tipo == 'microdatos':
            bd = símismo.microdatos
        elif tipo == 'datos':
            bd = símismo.datos
        else:
            raise ValueError
        if bd is None:
            return []
        if lugar is None:
            return bd['tiempo'].values
        else:
            return bd['tiempo'].where(bd['lugar'] == lugar, drop=True).values

    def tiempo_fecha(símismo):
        return np.issubdtype(símismo.tiempos().dtype, np.datetime64)

    def _validar_bd(símismo, bd):
        """
        Valida un nombre de base de datos.

        Parameters
        ----------
        bd: str | Datos | list[str | Datos].
            La base de datos para validar, o una lista de estas.

        Returns
        -------
        str:
            El nombre validado

        Raises
        ------
        ValueError
            Si no estaba conectada una base de datos correspondiente.

        """

        # Si no hay nada, devolver nada
        if bd is None:
            return None

        # Convertir a lista, si necesario
        if isinstance(bd, list):
            l_bd = bd
        else:
            l_bd = [bd]

        for í, b in enumerate(l_bd):
            # Convertir a nombre, si necesario.
            if isinstance(b, Datos):
                l_bd[í] = b.nombre

            # Verificaar que existe la base de datos.
            if l_bd[í] not in símismo.bds:
                raise ValueError(_('La base de datos "{}" no está conectada.').format(b))

        # Devolver el nombre validado.
        if isinstance(bd, list):
            return l_bd
        else:
            return l_bd[0]

    def _validar_var(símismo, var):
        """
        Valida el nombre de un variable, o una lista de nombres de variables.

        Parameters
        ----------
        var: str | list[str]
            El variable para verificar.

        Returns
        -------
        str | list[str]
            Los nombres de variables validados.
        """

        # Convertir a lista, si necesario
        if isinstance(var, list):
            l_var = var
        else:
            l_var = [var]

        for í, v in enumerate(l_var):
            # Verificar el nombre del variable
            if v not in símismo.variables:
                raise ValueError(_('El variable "{}" no existe.').format(var))

        # Devolver el nombre validado.
        if isinstance(var, list):
            return l_var
        else:
            return var

    def espec_var(símismo, var, var_bd=None, bds=None, var_err=None):
        """
        Crea un variable en la base de datos.

        Parameters
        ----------
        var: str
            El nombre del variable.
        var_bd: str
            El nombre de este variable en las bases de datos subyacentes, si difiere de `var`.
        bds: str | Datos | list[str | Datos]
            Las bases de datos en las cuales se encuentra este variable.
        var_err: str
            El nombre de otra columna en la base de datos con la magnitud del error en la medición
            de este variable.

        """

        # Si no se especificó nombre distinto, es que debe ser lo mismo.
        if var_bd is None:
            var_bd = var

        # Formatear la lista de bases de datos.
        if bds is None:
            bds = list(símismo.bds)  # Si no se especificó, las tomaremos todas.
        if not isinstance(bds, list):
            bds = [bds]  # Convertir a lista
        for í, bd in enumerate(bds.copy()):
            bds[í] = símismo._validar_bd(bd)  # Validar las bases de datos

        # Quitar las bases de datos que no contienen el variable de interés.
        for nm_bd in bds.copy():
            if var_bd not in símismo.bds[nm_bd].cols:
                avisar(_('"{}" no existe en base de datos "{}".').format(var_bd, nm_bd))
                bds.remove(nm_bd)

        # Si no quedan bases de datos, tenemos complicación.
        if not len(bds):
            raise ValueError('El variable "{}" no existe en cualquiera de las bases de datos especificadas.'
                             .format(var_bd))

        # Ahora, el verdadero trabajo.
        if var not in símismo.variables:
            # Si no existía el variable antes, crear su diccionario de una vez.
            símismo.variables[var] = {'fuente': {bd: {'var': var_bd} for bd in bds}}
        else:
            # Si ya existía, actualizar su diccionario existente.
            for bd in bds:
                símismo.variables[var]['fuente'][bd] = {'var': var_bd}

        # Agregar información de error
        for bd in bds:
            símismo.variables[var]['fuente'][bd]['col_error'] = var_err

        símismo.bd_lista = False

    def borrar_var(símismo, var, bds=None):
        """
        Borra un variable existente.

        Parameters
        ----------
        var: str
            El variable para borrar.
        bds: str | Datos | list[str | Datos]

        """

        # Verificar el nombre del variable
        var = símismo._validar_var(var)

        # Validar las bases de datos
        bds = símismo._validar_bd(bds)

        # Borrarlo
        if bds is None:
            # Si no se especificó la base de datos, borrar el variable entero.
            símismo.variables.pop(var)
        else:
            # Si se especificó la base de datos, borrar el variable únicamente para ésta
            if not isinstance(bds, list):
                bds = [bds]
            for bd in bds:
                símismo.variables[var]['fuente'].pop(bd)

        # Limpiamos nuestra base de datos interna.
        símismo._limp_vars()

    def renombrar_var(símismo, var, nuevo_nombre):
        """
        Cambia el nombre de un variable.

        Parameters
        ----------
        var: str
            El nombre actual del variable.
        nuevo_nombre: str
            El nuevo nombre.

        """

        # Validar el variable
        var = símismo._validar_var(var)

        # Verificar que el nuevo nombre no existe.
        if nuevo_nombre in símismo.variables:
            raise ValueError(_('El variable "{}" ya existe. Hay que borrarlo primero.').format(nuevo_nombre))

        # Cambiar el nombre
        símismo.variables[nuevo_nombre] = símismo.variables.pop(var)

        # Ya debemos actualizar nuestra base de datos interna.
        símismo.bd_lista = False

    def _limp_vars(símismo):
        """
        Limpia el diccionario de variables y las bases de datos internas.

        """

        # Asegurarse que no queden variables sin bases de datos en `SuperBD.variables`.
        for v in list(símismo.variables):
            d_v = símismo.variables[v]
            # Si no quedan bases de datos asociadas, quitar el variable ahora.
            if len(d_v['fuente']) == 0:
                símismo.variables.pop(v)

        # Para simplificar el código
        datos_ind = símismo.microdatos
        datos_reg = símismo.datos

        # Asegurarse que no queden variables (columas) en las bases de datos que no estén en `SuperBD.variables`.
        for bd_pd in [datos_ind, datos_reg]:
            # Para cada base de datos Pandas...
            if bd_pd is not None:
                # Si existe...
                for c in list(bd_pd):
                    # Para cada columna...
                    if c not in list(símismo.variables) + ['bd', 'lugar', 'tiempo']:
                        # Si ya no existe como variable, quitar la columna.
                        bd_pd.drop(c, axis=1, inplace=True)

        # Quitar observaciones que provienen de las bases de datos que ya no están vinculadas
        if símismo.microdatos is not None:
            símismo.microdatos = datos_ind[datos_ind['bd'].isin(símismo.bds)]
        if símismo.datos is not None:
            símismo.datos = datos_reg[datos_reg['bd'].isin(símismo.bds)]

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

    def _gen_bd_intern(símismo):
        """
        Genera las bases de datos internas.
        """

        # Primero, limpiar los variables
        símismo._limp_vars()

        # Borrar las bases de datos existentes
        símismo.microdatos = símismo.datos = símismo.datos_err = None

        bds_acronistas = {
            'microdatos': [],
            'datos': [],
            'datos_err': []
        }

        # Agregar datos
        for nmb, bd in símismo.bds.items():
            # Para cada base de datos vinculada...

            # Sacar los variables de interés para esta base de datos
            d_vars_interés = {v: d_v for v, d_v in símismo.variables.items() if nmb in d_v['fuente']}

            # Agregar los datos a las bases internas
            if len(d_vars_interés):

                # La lista de los nombres correspondientes en esta BD
                l_vars_bd = [d_v['fuente'][nmb]['var'] for _, d_v in d_vars_interés.items()]

                # Obtener los datos
                bd_temp = bd.obt_datos(l_vars=list(set(l_vars_bd)))

                # Convertir los nombres de los variables
                bd_temp_nv = bd_temp.rename(dict(zip(l_vars_bd, list(d_vars_interés))))
                for vr, nv in zip(l_vars_bd, list(d_vars_interés)):
                    if nv not in bd_temp_nv:
                        bd_temp_nv[nv] = bd_temp[vr]
                bd_temp = bd_temp_nv

                # MicroDatos
                if isinstance(bd, MicroDatos):
                    # Crear la BD o modificarla, según el caso.
                    if símismo.microdatos is None:
                        símismo.microdatos = bd_temp
                    else:
                        if símismo._con_tiempo(bd_temp):
                            símismo.microdatos = símismo._concat_bds_xr(bd_temp, símismo.microdatos)
                        else:
                            bds_acronistas['microdatos'].append(bd_temp)

                # Datos normales
                else:
                    # Crear la BD o modificarla, según el caso.
                    if símismo.datos is None:
                        símismo.datos = bd_temp
                    else:
                        if símismo._con_tiempo(bd_temp):
                            símismo.datos = símismo._concat_bds_xr(bd_temp, símismo.datos)
                        else:
                            bds_acronistas['datos'].append(bd_temp)

                    # Calcular errores
                    dic_errores = {}
                    for v, d_v in d_vars_interés.items():
                        dic_errores[v] = bd.obt_error(d_v['fuente'][nmb]['var'],
                                                      col_error=d_v['fuente'][nmb]['col_error'])
                    bd_err_temp = bd_temp.copy(deep=True)
                    for vr, err in dic_errores.items():
                        bd_err_temp[vr][:] = err

                    # Crear la BD o modificarla, según el caso.
                    if símismo.datos_err is None:
                        símismo.datos_err = bd_err_temp
                    else:
                        símismo.datos_err = símismo._concat_bds_xr(bd_err_temp, símismo.datos_err)

        for ll, l_bd in bds_acronistas.items():
            if ll == 'microdatos':
                símismo.microdatos = símismo._aplicar_acronistas(símismo.microdatos, l_bd)
            elif ll == 'datos':
                símismo.datos = símismo._aplicar_acronistas(símismo.datos, l_bd)
            else:
                símismo.datos_err = símismo._aplicar_acronistas(símismo.datos_err, l_bd)

        # Ya la base de datos sí está actualizada y lista para trabajar
        símismo.bd_lista = True

    def _aplicar_acronistas(símismo, bd_base, l_acrons):
        if not len(l_acrons):
            return bd_base

        bd_acron = l_acrons.pop(0)
        for bd in l_acrons:
            bd_acron = bd_acron.merge(bd)  # para hacer: verificar

        for vr in bd_acron.data_vars:
            if vr in bd_base.data_vars:
                raise ValueError('Bases de datos múltiples con datos para "{}", un variable no temporal.'.format('vr'))
            bd_base = bd_base.assign(**{vr: ('n', [np.nan] * len(bd_base['n']))})
            for i, lg in enumerate(bd_acron['lugar'].values):
                bd_base[vr].values[np.where(bd_base['lugar'].values == lg)] = bd_acron[vr][i]

        return bd_base

    @staticmethod
    def _concat_bds_xr(bd1, bd2):

        faltan_en_1 = [x for x in bd2.data_vars if x not in bd1.data_vars]
        faltan_en_2 = [x for x in bd1.data_vars if x not in bd2.data_vars]
        n_1 = len(bd1['n'])
        n_2 = len(bd2['n'])
        bd1 = bd1.assign(**{v: ('n', [np.nan] * n_1) for v in faltan_en_1})
        bd2 = bd2.assign(**{v: ('n', [np.nan] * n_2) for v in faltan_en_2})

        return xr.concat([bd1, bd2], 'n')

    @staticmethod
    def _con_tiempo(bd_xr):
        return not np.all(np.equal(bd_xr['tiempo'].values, np.datetime64('NaT')))

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
            bd_sel = bd_sel.set_index(m=['lugar', 'tiempo']).groupby('m').mean()
            bd_sel = bd_sel.assign(**{'lugar': ('n', bd_sel['m_level_0']), 'tiempo': ('n', bd_sel['m_level_1'])})
            bd_sel = bd_sel.drop('m')
            bd_sel = bd_sel.set_coords(['lugar', 'tiempo'])
            bd_sel = xr.Dataset(data_vars={vr: ('n', bd_sel[vr].values) for vr in bd_sel.data_vars},
                                coords={vr: ('n', bd_sel[vr].values) for vr in bd_sel.coords})

        # Excluir las observaciones que faltan
        if excl_faltan:
            # Si excluyemos las observaciones que faltan, guardar únicamente las filas con observacienes
            # para todos los variables
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

    @staticmethod
    def _filtrar_tiempo(bd, tiempos):
        """
        Filtra una base de datos Pandas por fecha.

        Parameters
        ----------
        bd: xr.Dataset
            La base de datos. Debe contener las columnas `fecha` y `bd`.
        tiempos: str | tuple | list | ft.date | ft.datetime
            La fecha o fechas de interés. Si es una tupla, se interpretará como **rango de interés**, si es lista,
            se interpretará como lista de fechas de interés **individuales**.

        Returns
        -------
        pd.DataFrame:
            La base de datos filtrada e interpolada.

        """

        # Escoger las columnas que corresponden a las tiempos deseadas.
        if isinstance(tiempos, tuple):
            if tiempos[0] is not None:
                bd = bd.where(bd['tiempo'] >= tiempos[0], drop=True)
            if tiempos[1] is not None:
                bd = bd.where(bd['tiempo'] <= tiempos[1], drop=True)
            return bd
        elif isinstance(tiempos, list):
            return bd.where(bd['tiempo'].isin(tiempos), drop=True)
        else:
            return bd.where(bd['tiempo'] == tiempos, drop=True)

    def graficar_hist(símismo, var, fechas=None, lugar=None, bd_datos=None, tipo='datos', archivo=None):

        tipo = tipo.lower()

        if archivo is None:
            archivo = var + '.jpg'
        archivo = símismo._validar_archivo(archivo, ext='.jpg')

        datos = símismo.obt_datos(l_vars=var, lugares=lugar, bd_datos=bd_datos, tiempos=fechas, tipo=tipo)

        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)
        ejes.set_aspect('equal')

        ejes.set_xlabel(var)
        ejes.set_ylabel(_('Freq'))

        ejes.set_title(var)

        ejes.hist(datos[var])

        fig.savefig(archivo)

    def graficar_línea(símismo, var, fechas=None, lugar=None, bd_datos=None, archivo=None):

        if archivo is None:
            archivo = var + '.jpg'
        archivo = símismo._validar_archivo(archivo, ext='.jpg')

        datos = símismo.obt_datos(l_vars=var, tiempos=fechas, lugares=lugar, bd_datos=bd_datos, tipo='datos')
        datos_error = símismo.obt_datos(l_vars=var, tiempos=fechas, lugares=lugar, bd_datos=bd_datos, tipo='error')

        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)

        fechas = datos['tiempo']
        n_fechas = len(np.unique(fechas.values))
        lugares = np.unique(datos['lugar']).tolist()  # type: list
        n_lugares = len(lugares)

        if n_fechas > 1:
            for l in lugares:
                y = datos.where(datos['lugar'] == l, drop=True)[var].values
                fechas_l = datos.where(datos['lugar'] == l, drop=True)['tiempo'].values
                err = datos_error.where(datos_error['lugar'] == l, drop=True)[var].values

                l = ejes.plot_date(fechas_l, y, label=l, fmt='-')
                if err.shape == y.shape:
                    color = l[0].get_color()
                    ejes.fill_between(fechas_l, y - err / 2, y + err / 2, facecolor=color, alpha=0.5)

            ejes.set_xlabel(_('tiempo'))
            ejes.set_ylabel(var)

        else:
            ejes.bar(range(n_lugares), datos[var])
            ejes.set_ylabel(var)
            ejes.set_xlabel(_('Lugar'))
            ejes.set_xticks(range(n_lugares))
            ejes.set_xticklabels(lugares)

        ejes.legend()
        ejes.set_title(var)
        fig.savefig(archivo)

    def graf_comparar(símismo, var_x, var_y, fechas=None, lugar=None, bd_datos=None, archivo=None):

        if archivo is None:
            archivo = var_x + '_' + var_y + '.jpg'
        archivo = símismo._validar_archivo(archivo, ext='.jpg')

        datos = símismo.obt_datos(l_vars=[var_x, var_y], lugares=lugar, bd_datos=bd_datos, tiempos=fechas)

        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)

        ejes.scatter(datos[var_x], datos[var_y])

        ejes.set_xlabel(var_x)
        ejes.set_ylabel(var_y)

        ejes.set_title(_('{} vs {}').format(var_x, var_y))
        fig.savefig(archivo)

    def guardar_datos(símismo, archivo=''):
        """
        Guarda los datos en formato json, el cual queda fácil para vcargar de nuevo en Tinamït.

        Parameters
        ----------
        archivo: str
            El fuente en el cual guardar los datos.

        """

        # Preparar el nombre de fuente
        archivo = símismo._validar_archivo(archivo, ext='.json')

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        # Convertir los datos a json
        dic = {'ind': símismo.microdatos.to_dict(),
               'reg': símismo.datos.to_dict(),
               'err': símismo.datos_err.to_dict()}
        jsonificar(dic)

        # Guardar en UTF-8
        guardar_json(dic, arch=archivo)

    def _validar_archivo(símismo, archivo='', ext=None, debe_existir=False):

        archivo = os.path.abspath(archivo)

        if ext is not None:
            if ext[0] != '.':
                ext = '.' + ext

            if not len(os.path.splitext(archivo)[1]):
                archivo = os.path.join(archivo, símismo.nombre + ext)

        if debe_existir and not os.path.isfile(archivo):
            raise FileNotFoundError(_('El fuente "{}" no existe.').format(archivo))
        else:
            if ext:
                directorio = os.path.split(archivo)[0]
            else:
                directorio = archivo
            if not os.path.isdir(directorio):
                os.makedirs(directorio)

        return archivo

    def cargar_datos(símismo, archivo=''):

        archivo = símismo._validar_archivo(archivo, ext='.json', debe_existir=True)
        dic = cargar_json(archivo)

        símismo.microdatos = xr.Dataset.from_dict(dic['ind'])
        símismo.datos = xr.Dataset.from_dict(dic['reg'])
        símismo.datos_err = xr.Dataset.from_dict(dic['err'])
        for bd in [símismo.microdatos, símismo.datos, símismo.datos_err]:
            bd['tiempo'] = ('n', np.array(bd['tiempo'], dtype='datetime64'))
            bd['lugar'] = ('n', bd['lugar'].astype(str))

    def borrar_archivo_datos(símismo, archivo=''):

        archivo = símismo._validar_archivo(archivo, ext='.json', debe_existir=True)

        os.remove(archivo)

    def exportar_datos_csv(símismo, directorio=''):

        directorio = símismo._validar_archivo(directorio)

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        for nmb, bd in {
            'ind': símismo.microdatos, 'reg': símismo.datos, 'error_reg': símismo.datos_err
        }.items():
            archivo = os.path.join(directorio, símismo.nombre + '_' + nmb + '.csv')
            bd.to_dataframe().to_csv(archivo)

    def __contains__(símismo, item):
        return item in símismo.variables


def gen_SuperBD(datos):
    if isinstance(datos, SuperBD):
        return datos
    elif isinstance(datos, Datos):
        return SuperBD('Autogen', bds=datos)
    elif isinstance(datos, (pd.DataFrame, dict, xr.Dataset)):
        return SuperBD('Autogen', bds=Datos('Autogen', datos))
    else:
        raise TypeError(_('Tipo de datos "{}" no reconocido.').format(type(datos)))


def _gen_bd(archivo, cód_vacío):
    """

    Parameters
    ----------
    archivo : str | dict | pd.DataFrame | xr.Dataset

    Returns
    -------

    """

    if isinstance(archivo, pd.DataFrame):
        return BDpandas(archivo, cód_vacío)

    elif isinstance(archivo, dict):
        return BDdic(archivo, cód_vacío)

    elif isinstance(archivo, xr.Dataset):
        return BDxr(archivo, cód_vacío)

    elif isinstance(archivo, str):
        ext = os.path.splitext(archivo)[1]

        if ext == '.txt' or ext == '.csv':
            return BDtexto(archivo, cód_vacío)
        else:
            raise ValueError(_('Formato de base de datos "{}" no reconocido.').format(ext))


def jsonificar(o):
    if isinstance(o, dict):
        for ll, v in o.items():
            if isinstance(v, (dict, list)):
                jsonificar(v)
            elif isinstance(v, (ft.date, ft.datetime)):
                o[ll] = str(v)
            elif isinstance(v, np.ndarray):
                o[ll] = v.tolist()
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, (dict, list)):
                jsonificar(v)
            elif isinstance(v, (ft.date, ft.datetime)):
                o[i] = str(v)
            elif isinstance(v, np.ndarray):
                o[i] = v.tolist()


def numpyficar(d):
    for ll, v in d.items():
        if isinstance(v, dict):
            numpyficar(v)
        elif isinstance(v, list):
            try:
                d[ll] = np.array(v, dtype=float)
            except ValueError:
                pass


class BD(object):
    """
    Una superclase para lectores de bases de datos.
    """

    def __init__(símismo, fuente, cód_vacío=None):
        símismo.fuente = fuente
        if cód_vacío is None:
            símismo.cód_vacío = ['na', 'NA', 'NaN', 'nan', '']
        else:
            símismo.cód_vacío = cód_vacío

        if isinstance(fuente, str) and not os.path.isfile(fuente):
            raise FileNotFoundError(_('El fuente "{}" no existe.').format(fuente))

        símismo.n_obs = símismo.calc_n_obs()

    def obt_nombres_cols(símismo):
        """

        :return:
        :rtype: list[str]
        """
        raise NotImplementedError

    def obt_datos(símismo, cols):
        """

        Parameters
        ----------
        cols :

        Returns
        -------
        dict[str, np.ndarray]
        """

        if not isinstance(cols, list):
            cols = [cols]

        datos = símismo._obt_datos(cols)
        for var, val in datos.items():
            val[np.isin(val, símismo.cód_vacío)] = np.nan
            datos[var] = val.astype(float)

        return datos

    def _obt_datos(símismo, cols):

        raise NotImplementedError

    def obt_datos_tx(símismo, col):
        """

        :param col:
        :type col: list[str] | str
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
        fechas_tx = símismo.obt_datos_tx(col=cols)

        # Procesar la lista de fechas
        return símismo._leer_fechas(lista_fechas=fechas_tx)

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


class BDtexto(BD):
    """
    Una clase para leer bases de datos en formato texto delimitado por comas (.csv).
    """

    def __init__(símismo, fuente, cód_vacío=None):

        símismo.codif = detectar_codif(fuente, máx_líneas=1)
        super().__init__(fuente=fuente, cód_vacío=cód_vacío)

    def calc_n_obs(símismo):
        """

        :rtype: int
        """
        with open(símismo.fuente, encoding=símismo.codif) as d:
            n_filas = sum(1 for f in d if len(f)) - 1  # Sustrayemos la primera fila

        return n_filas

    def _obt_datos(símismo, cols):

        m_datos = np.empty((len(cols), símismo.n_obs))

        with open(símismo.fuente, encoding=símismo.codif) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                m_datos[:, n_f] = [tx_a_núm(f[c].strip()) if f[c].strip() not in símismo.cód_vacío else np.nan for c in
                                   cols]

        return {c: m_datos[i] for i, c in enumerate(cols)}

    def obt_datos_tx(símismo, col):
        """

        :param col:
        :type col: list[str] | str
        :return:
        :rtype: list
        """
        if not isinstance(col, list):
            col = [col]

        l_datos = [[''] * símismo.n_obs] * len(col)

        with open(símismo.fuente, encoding=símismo.codif) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                for i_c, c in enumerate(col):
                    l_datos[i_c][n_f] = f[c]

        if len(col) == 1:
            l_datos = l_datos[0]

        return l_datos

    def obt_nombres_cols(símismo):
        """

        :return:
        :rtype: list[str]
        """

        with open(símismo.fuente, encoding=símismo.codif) as d:
            lector = csv.reader(d)

            nombres_cols = next(lector)

        return nombres_cols


class BDxr(BD):
    def obt_nombres_cols(símismo):
        return list(símismo.fuente.data_vars)

    def _obt_datos(símismo, cols):
        datos = {c: símismo.fuente[c].values for c in cols}
        for c, v in datos.items():
            if np.issubdtype(v.dtype, np.str_):
                datos[c] = v.astype(object)
            else:
                datos[c] = v.astype(float)
        return datos

    def obt_datos_tx(símismo, col):
        return símismo.fuente[col].astype(object).values

    def calc_n_obs(símismo):
        var = símismo.obt_nombres_cols()[0]
        return símismo.fuente[var].shape[0]


class BDpandas(BD):

    def obt_nombres_cols(símismo):
        return list(símismo.fuente)

    def _obt_datos(símismo, cols):
        return {c: símismo.fuente[c].values.astype(object) for c in cols}

    def obt_datos_tx(símismo, col):
        return símismo.fuente[col].values.astype(str).tolist()

    def calc_n_obs(símismo):
        return len(símismo.fuente)


class BDdic(BD):

    def __init__(símismo, fuente, cód_vacío=None):

        if all(isinstance(v, dict) for v in fuente.values()):
            for lg, d_l in fuente.items():
                if len(set(len(v) for v in d_l.items())) != 1:
                    raise ValueError(_('Todos los variables en el lugar "{}" deben tener el mismo tamaño.').format(lg))
            n_obs = [len(list(d_l.values())[0]) for d_l in fuente.values()]
            c_vars = set(v for d_v in fuente.values() for v in d_v)
            lugs = list(fuente)
            datos_fin = {var: np.concatenate([fuente[lg][var] for lg in fuente]) for var in c_vars}
            datos_fin['lugar'] = np.concatenate([[lg] * n for n, lg in zip(n_obs, lugs)])
        elif not any(isinstance(v, dict) for v in fuente.values()):
            datos_fin = fuente

        else:
            raise ValueError(_('Error en el formato del diccionario de datos. :('))

        super().__init__(fuente=datos_fin, cód_vacío=cód_vacío)

    def obt_nombres_cols(símismo):
        return list(símismo.fuente)

    def _obt_datos(símismo, cols):
        datos = {c: np.array(símismo.fuente[c]) for c in cols}
        for c, v in datos.items():
            if np.issubdtype(v.dtype, np.str_):
                datos[c] = v.astype(object)
            else:
                datos[c] = v.astype(float)
        return datos

    def obt_datos_tx(símismo, col):
        return np.array(símismo.fuente[col]).astype(str).tolist()

    def calc_n_obs(símismo):
        return len(list(símismo.fuente.values())[0])


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
        if all(len(f) == 7 for f in lista_fechas):
            lista_fechas = [f + '-01' for f in lista_fechas]
        elif all(len(f) == 4 for f in lista_fechas):
            lista_fechas = [f + '-01-01' for f in lista_fechas]

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
