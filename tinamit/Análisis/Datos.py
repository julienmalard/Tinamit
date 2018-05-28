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
        :rtype: pd.DataFrame

        """

        códs_vacío_final = símismo.cód_vacío.copy()
        if cód_vacío is not None:
            if isinstance(cód_vacío, list) or isinstance(cód_vacío, set):
                códs_vacío_final.update(cód_vacío)
            else:
                códs_vacío_final.add(cód_vacío)

        # Obtener los datos en formato NumPy
        datos_np = símismo.bd.obt_datos(l_vars, cód_vacío=códs_vacío_final)

        # Convertir en formato Pandas
        bd_pd = pd.DataFrame(datos_np.T, columns=l_vars)

        # Agregar una columna con el nombre de la base de datos y el lugar o lugares de observación
        bd_pd['bd'] = símismo.nombre
        bd_pd['lugar'] = símismo.lugares

        # Agregar la fecha de observación
        fechas = símismo.fechas
        if isinstance(fechas, tuple):
            # Puede ser...
            if fechas[0] is not None:
                # Una fecha original y una secuencia de no. de días relativos a la fecha original
                bd_pd['fecha'] = pd.to_datetime(fechas[0]) + pd.to_timedelta(fechas[1], unit='d')
            else:
                # Una lista de años
                bd_pd['fecha'] = pd.to_datetime(['{}-1-1'.format(str(x)) for x in fechas[1]])
        elif fechas is None:
            # Puede ser que no haya fecha
            bd_pd['fecha'] = None
        else:
            # ...o puede ser que estén en formato de texto
            bd_pd['fecha'] = pd.to_datetime(símismo.fechas)

        return bd_pd

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
    """
    Una :class:`SuperBD` reune varias bases de :class:`Datos` en un lugar cómodo para acceder a los datos.
    """

    def __init__(símismo, nombre, bds=None, geog=None):
        """

        Parameters
        ----------
        nombre: str
            El nombre de la base de datos.
        bds: list[Datos]
            Una lista opcional de bases de :class:`Datos` para conectar.
        geog: Geografía
            Una :class:`Geografía` opcional que corresponde con los datos.
        """

        # Guardar el nombre y la geografía
        símismo.nombre = nombre
        símismo.geog = geog

        # Guardar las bases de datos
        if bds is None:
            símismo.bds = {}  # type: dict[Datos]
        else:
            if isinstance(bds, Datos):
                bds = [bds]
            símismo.bds = {d.nombre: d for d in bds}  # type: dict[str, Datos]

        # Información de variables (y de sus bases de datos correspondientes)
        símismo.vars = {}

        # Bases de datos internas
        símismo.datos_reg = None  # type: pd.DataFrame
        símismo.datos_reg_err = None  # type: pd.DataFrame
        símismo.datos_ind = None  # type: pd.DataFrame

        # Si nuesta base de datos interna está actualizada o no.
        símismo.bd_lista = False

    def conectar_datos(símismo, bd, auto_conectar=True, bd_plantilla=None):
        """
        Agregar una base de datos.

        Parameters
        ----------
        bd: Datos
            Los datos para agregar.
        auto_conectar: bool
            Si conectamos las columnas de esta nueva base de datos automáticamente.
        bd_plantilla: Datos | str | list[Datos | str]
            Otra base existente (opcional) para emplear como plantilla para conectar los variables
            de `bd`. No tiene efecto si `auto_conectar` es ``False``.

        """

        # Avisar si existía antes.
        if bd.nombre in símismo.bds:
            avisar(_('Ya existía la base de datos "{}". Borramos la que estaba antes.').format(bd))

        # Agregar la base de datos
        símismo.bds[bd.nombre] = bd

        # Conectar los variables automáticamente, si queremos
        if auto_conectar:
            símismo.auto_llenar(bd=bd, bd_plantilla=bd_plantilla)

        # Nuestras bases de datos internas ya no están actualizadas
        símismo.bd_lista = False

    def auto_llenar(símismo, bd, bd_plantilla):
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
        for var, d_var in símismo.vars.items():
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
        for var, d_var in símismo.vars.items():
            try:
                d_var['fuente'].pop(bd)
            except KeyError:
                pass

        # Nuestas bases de datos internas ya necesitan ser actualizadas.
        símismo.bd_lista = False

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
            if v not in símismo.vars:
                raise ValueError(_('El variable "{}" no existe.').format(var))

        # Devolver el nombre validado.
        if isinstance(var, list):
            return l_var
        else:
            return var

    def espec_var(símismo, var, var_bd=None, bds=None, cód_vacío='', var_err=None):
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
        cód_vacío: str | list[str]
            El código que corresponde a un valor que falta en la base de datos.
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
        if var not in símismo.vars:
            # Si no existía el variable antes, crear su diccionario de una vez.
            símismo.vars[var] = {'fuente': {bd: {'var': var_bd, 'cód_vacío': cód_vacío} for bd in bds}}
        else:
            # Si ya existía, actualizar su diccionario existente.
            for bd in bds:
                símismo.vars[var]['fuente'][bd] = {'var': var_bd, 'cód_vacío': cód_vacío}

        # Agregar información de error para bases de datos regionales
        for bd in bds:
            if isinstance(símismo.bds[bd], DatosRegión):
                símismo.vars[var]['fuente'][bd]['col_error'] = var_err

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
            símismo.vars.pop(var)
        else:
            # Si se especificó la base de datos, borrar el variable únicamente para ésta
            if not isinstance(bds, list):
                bds = [bds]
            for bd in bds:
                símismo.vars[var]['fuente'].pop(bd)

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
        if nuevo_nombre in símismo.vars:
            raise ValueError(_('El variable "{}" ya existe. Hay que borrarlo primero.').format(nuevo_nombre))

        # Cambiar el nombre
        símismo.vars[nuevo_nombre] = símismo.vars.pop(var)

        # Ya debemos actualizar nuestra base de datos interna.
        símismo.bd_lista = False

    def _limp_vars(símismo):
        """
        Limpia el diccionario de variables y las bases de datos internas.

        """

        # Asegurarse que no queden variables sin bases de datos en `SuperBD.vars`.
        for v in list(símismo.vars):
            d_v = símismo.vars[v]
            # Si no quedan bases de datos asociadas, quitar el variable ahora.
            if len(d_v['fuente']) == 0:
                símismo.vars.pop(v)

        # Para simplificar el código
        datos_ind = símismo.datos_ind
        datos_reg = símismo.datos_reg

        # Asegurarse que no queden variables (columas) en las bases de datos que no estén en `SuperBD.vars`.
        for bd_pd in [datos_ind, datos_reg]:
            # Para cada base de datos Pandas...
            if bd_pd is not None:
                # Si existe...
                for c in list(bd_pd):
                    # Para cada columna...
                    if c not in list(símismo.vars) + ['bd', 'lugar', 'fecha']:
                        # Si ya no existe como variable, quitar la columna.
                        bd_pd.drop(c, axis=1, inplace=True)

        # Quitar observaciones que provienen de las bases de datos que ya no están vinculadas
        if símismo.datos_ind is not None:
            símismo.datos_ind = datos_ind[datos_ind['bd'].isin(símismo.bds)]
        if símismo.datos_reg is not None:
            símismo.datos_reg = datos_reg[datos_reg['bd'].isin(símismo.bds)]

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
        ft.date | ft.datetime | str | list | tuple:
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

            if isinstance(fch, ft.date) or isinstance(fch, ft.datetime):
                return fch

            elif isinstance(fch, int):
                return ft.date(year=fch, month=1, day=1)

            elif isinstance(fch, str):
                try:
                    ft.datetime.strptime(fch, '%Y-%m-%d').date()
                    return fch
                except ValueError:
                    raise ValueError(_('La fecha "{}" no está en el formato "AAAA-MM-DD"').format(fch))

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
            for f in fechas:
                verificar_fecha(f)

        elif isinstance(fechas, list):
            # El caso de una lista de fechas de interés

            # Verificar que las fechas sean válidas
            for f in fechas:
                verificar_fecha(f)

        else:
            # Sino, tenemos una única fecha
            verificar_fecha(fechas)

        return fechas

    def _gen_bd_intern(símismo):
        """
        Genera las bases de datos internas.
        """

        # Primero, limpiar los variables
        símismo._limp_vars()

        # Borrar las bases de datos existentes
        símismo.datos_ind = símismo.datos_reg = None

        # Agregar datos
        for nmb, bd in símismo.bds.items():
            # Para cada base de datos vinculada...

            # Sacar los variables de interés para esta base de datos
            d_vars_interés = {v: d_v for v, d_v in símismo.vars.items() if nmb in d_v['fuente']}

            # Agregar los datos a las bases internas
            if len(d_vars_interés):

                # La lista de los nombres correspondientes en esta BD
                l_vars_bd = [d_v['fuente'][nmb]['var'] for _, d_v in d_vars_interés.items()]

                # La lista de los códigos de datos vacíos corresondientes
                l_códs_vac = [d_v['fuente'][nmb]['cód_vacío'] for _, d_v in d_vars_interés.items()]

                # Obtener los datos
                bd_pds_temp = bd.obt_datos(l_vars=l_vars_bd, cód_vacío=l_códs_vac)

                # Convertir los nombres de los variables
                bd_pds_temp.rename(
                    index=str,
                    columns={nmb: nv_nmb for nmb, nv_nmb in zip(l_vars_bd, list(d_vars_interés))},
                    inplace=True
                )

                # Datos individuales
                if isinstance(bd, DatosIndividuales):
                    # Crear la BD o modificarla, según el caso.
                    if símismo.datos_ind is None:
                        símismo.datos_ind = bd_pds_temp
                    else:
                        símismo.datos_ind = pd.concat([bd_pds_temp, símismo.datos_ind], ignore_index=True)

                # Datos regionales
                elif isinstance(bd, DatosRegión):
                    # Crear la BD o modificarla, según el caso.
                    if símismo.datos_reg is None:
                        símismo.datos_reg = bd_pds_temp
                    else:
                        símismo.datos_reg = pd.concat([bd_pds_temp, símismo.datos_reg], ignore_index=True)

                    # Calcular errores
                    datos_err = np.array(
                        [bd.obt_error(d_v['fuente'][nmb]['var'], col_error=d_v['fuente'][nmb]['col_error'])
                         for v, d_v in d_vars_interés.items()]
                    ).T
                    bd_pds_err_temp = bd_pds_temp.copy()
                    bd_pds_err_temp[list(d_vars_interés)] = datos_err

                    # Crear la BD o modificarla, según el caso.
                    if símismo.datos_reg_err is None:
                        símismo.datos_reg_err = bd_pds_temp
                    else:
                        símismo.datos_reg_err.append(bd_pds_temp, ignore_index=True)

        # Ya la base de datos sí está actualizada y lista para trabajar
        símismo.bd_lista = True

    def obt_datos(símismo, l_vars, lugar=None, bd_datos=None, fechas=None, excl_faltan=False,
                  tipo='individual'):
        """

        Parameters
        ----------
        l_vars: str | list[str]
        lugar: str
        bd_datos: str | Datos | list[str | Datos]
        fechas: ft.date | str | list[ft.data | str]
        excl_faltan: bool
        tipo: str

        Returns
        -------

        """
        # Formatear la lista de variables deseados
        l_vars = símismo._validar_var(l_vars)
        if not isinstance(l_vars, list):
            l_vars = [l_vars]

        # Formatear el código de lugar
        if lugar is not None:
            if not isinstance(lugar, list):
                lugar = [lugar]

        # Formatear los datos
        bd_datos = símismo._validar_bd(bd_datos)
        if not isinstance(bd_datos, list):
            bd_datos = [bd_datos]

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        if tipo == 'individual':
            bd = símismo.datos_ind
        elif tipo == 'regional':
            bd = símismo.datos_reg
        elif tipo == 'error regional':
            bd = símismo.datos_reg_err
        else:
            raise ValueError

        # Asegurarse que existe esta base de datos
        if bd is None:
            raise ValueError

        # Seleccionar los variables de interés
        bd_sel = bd[l_vars + ['bd', 'fecha', 'lugar']]

        # Seleccionar las observaciones que vienen de la base de datos subyacente de interés
        if bd_datos is not None:
            bd_sel = bd_sel[bd_sel['bd'].isin(bd_datos)]

        # Seleccionar las observaciones que corresponden al lugar de interés
        if lugar is not None:
            bd_sel = bd_sel[bd_sel['lugar'].isin(lugar)]

        # Seleccionar las observaciones en las fechas de interés, e interpolar si necesario
        if fechas is not None:
            col_id = 'lugar' if tipo in ['regional', 'error regional'] else None
            bd_sel = símismo._filtrar_fechas(bd_sel, fechas, interpol_en=col_id)

        # Excluir las observaciones que faltan
        if excl_faltan:
            # Si excluyemos las observaciones que faltan, guardar únicamente las filas con observacienes
            # para todos los variables
            bd_sel.dropna(subset=[x for x in bd_sel.columns if x not in ['fecha', 'bd', 'lugar']],
                          inplace=True)
        else:
            # Sino, exlcuir únicamente las filas que faltans observaciones para todos los variables
            bd_sel.dropna(subset=[x for x in bd_sel.columns if x not in ['fecha', 'bd', 'lugar']],
                          how='all', inplace=True)

        return bd_sel

    def _filtrar_fechas(símismo, bd_pds, fechas, interpol_en=None):
        """
        Filtra una base de datos Pandas por fecha, e interpola si necesario.

        Parameters
        ----------
        bd_pds: pd.DataFrame
            La base de datos. Debe contener las columnas `fecha` y `bd`.
        fechas: str | tuple | list | ft.date | ft.datetime
            La fecha o fechas de interés. Si es una tupla, se interpretará como **rango de interés**, si es lista,
            se interpretará como lista de fechas de interés **individuales**.
        interpol_en: str
            La columna de categoría (por ejemplo, el lugar) con la cual hay que interpolar. Si es ``None``, no se
            interpolará.

        Returns
        -------
        pd.DataFrame:
            La base de datos filtrada e interpolada.

        """

        # Preparar las fechas
        fechas = símismo._validar_fechas(fechas)

        if interpol_en is None:
            # Si no podemos interpolar, simplemente escoger las columnas que corresponden a las fechas deseadas.
            if isinstance(fechas, tuple):
                return bd_pds.loc[(bd_pds['fecha'] >= fechas[0]) & (bd_pds['fecha'] <= fechas[1])]
            elif isinstance(fechas, list):
                return bd_pds.loc[(bd_pds['fecha'].isin(fechas))]
            else:
                return bd_pds.loc[(bd_pds['fecha'] == fechas)]
        else:

            # Si hay que interpolar, tenemos trabajo
            if interpol_en not in bd_pds:
                raise ValueError

            # Categorías únicas en las cuales interpolar (por ejemplo, interpolar para cada lugar).
            categs_únicas = bd_pds[interpol_en].unique()

            # Los variables para interpolar
            l_vars = [x for x in bd_pds if x not in [categs_únicas, 'fecha', 'bd']]

            if isinstance(fechas, tuple):
                raise NotImplementedError
            elif isinstance(fechas, list):
                fechas_interés = fechas
            else:
                fechas_interés = [fechas]

            # Para hacer: tomar cuenta de `fechas`

            # Calcular las interpolaciones
            finalizados = None

            # Para cada categoría...
            for c in categs_únicas:
                # Calcular el promedio de los valores de observaciones por categoría y por fecha
                proms_fecha = bd_pds.loc[bd_pds[interpol_en] == c].groupby(['fecha']).mean()  # type: pd.DataFrame

                # Si quedamos con datos...
                if proms_fecha.shape[0] > 0:

                    # Aplicar valores para variables sin fechas asociadas
                    sin_fecha = bd_pds[bd_pds.fecha.isnull()]
                    if sin_fecha.shape[0] > 0:
                        proms_sin_fecha = sin_fecha.loc[sin_fecha[categs_únicas] == c].mean().to_frame().T
                        proms_fecha.fillna(
                            value={ll: v[0] for ll, v in proms_sin_fecha.to_dict(orient='list').items()},
                            inplace=True
                        )

                    # Ahora, interpolar
                    mín = proms_fecha.index.min()  # Fecha mínima
                    máx = proms_fecha.index.max()  # Fecha máxima

                    # Calcular el rango temporal en el cual tenemos datos para todos los variables
                    for v in l_vars:
                        # Para cada variable...

                        # Las fechas para las cuales tenemos observaciones
                        compl_v = proms_fecha.dropna(subset=[v])[v]

                        # Las fechas máximas y mínimas para este variable
                        mín_v = compl_v.index.min()
                        máx_v = compl_v.index.max()

                        # Ajustar el máximo y mínimo global
                        mín = max(mín, mín_v)
                        máx = min(máx, máx_v)

                    # Las fechas en la base de datos para las cuales podemos interpolar
                    l_fechas_fin = [í for í in proms_fecha.index if mín <= í <= máx]

                    if len(l_fechas_fin):
                        # Si podemos interpolar...

                        # Agregar nuevas filas para los valores interpolados, si necesario.
                        nuevas_filas = pd.DataFrame(
                            columns=l_vars,
                            index=pd.to_datetime(
                                [x for x in l_fechas_fin if x not in proms_fecha.index])  # Únicament nuevas fechas
                        )

                        # Agregar las nuevas filas
                        proms_fecha = proms_fecha.append(nuevas_filas)

                        # Ordenar
                        proms_fecha = proms_fecha.sort_index()

                        # Por fin, interpolar
                        proms_fecha = proms_fecha.interpolate(method='time')

                        # Aplicar la categoría actual a las nuevas filas
                        proms_fecha[categs_únicas] = c

                        # Sacar únicamente las fechas de interés.
                        proms_fecha = proms_fecha.loc[l_fechas_fin]

                    else:
                        # Si no pudimos interpolar correctamente...
                        # Para hacer: si podemos interpolar solamente una parte de `fechas`
                        avisar('No se pudo interpolar entre datos "{}". Nos basaremos simplemente en los datos '
                               'observados sin tener cuenta de la fecha de observación.'.format(l_vars))

                        # Ordenar
                        proms_fecha = proms_fecha.sort_index()

                        # Interpolar lo mejor que pudimos
                        proms_fecha.interpolate(limit_direction='both', inplace=True)

                    # Agregar a los resultados finales
                    if finalizados is None:
                        finalizados = proms_fecha.dropna(how='any')  # Quitar datos que faltan #para hacer: ¿por qué?
                    else:
                        finalizados = finalizados.append(proms_fecha.dropna(how='any'))

            return finalizados

    def graficar(símismo, var, fechas=None, cód_lugar=None, lugar=None, datos=None, escala=None, archivo=None):

        dic_datos = símismo.obt_datos(l_vars=var, fechas=fechas, cód_lugar=cód_lugar, lugar=lugar, bd_datos=datos,
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
        datos = símismo.obt_datos(l_vars=[var_x, var_y], lugar=lugar, cód_lugar=cód_lugar, bd_datos=datos,
                                  fechas=fechas,
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

    def guardar_datos(símismo, archivo=''):
        """
        Guarda los datos en formato json, el cual queda fácil para vcargar de nuevo en Tinamït.

        Parameters
        ----------
        archivo: str
            El archivo en el cual guardar los datos.

        """

        # Preparar el nombre de archivo
        archivo = símismo._validar_archivo(archivo, ext='.json')

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        # Convertir los datos a json
        dic = {'ind': símismo.datos_ind.to_json(), 'reg': símismo.datos_reg.to_json(),
               'err': símismo.datos_reg_err.to_json()}

        # Guardar en UTF-8
        with open(archivo, 'w', encoding='UTF-8') as d:
            json.dump(dic, d, ensure_ascii=False)

    def _validar_archivo(símismo, archivo='', ext=None, debe_existir=False):

        archivo = os.path.abspath(archivo)

        if ext is not None:
            if not len(os.path.splitext(archivo)[1]):
                archivo = os.path.join(archivo, símismo.nombre + ext)

        if debe_existir and not os.path.isfile(archivo):
            raise ValueError
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

        with open(archivo, encoding='UTF-8') as d:
            dic = json.load(d)

        símismo.datos_ind = pd.read_json(dic['ind'])
        símismo.datos_reg = pd.read_json(dic['reg'])
        símismo.datos_reg_err = pd.read_json(dic['err'])

    def borrar_archivo_datos(símismo, archivo=''):

        archivo = símismo._validar_archivo(archivo, ext='.json', debe_existir=True)

        os.remove(archivo)

    def exportar_datos_csv(símismo, directorio=''):

        directorio = símismo._validar_archivo(directorio)

        # Actualizar las bases de datos, si necesario
        if not símismo.bd_lista:
            símismo._gen_bd_intern()

        for nmb, bd_pd in {
            'ind': símismo.datos_ind, 'reg': símismo.datos_reg, 'error_reg': símismo.datos_reg_err
        }.items():
            archivo = os.path.join(directorio, símismo.nombre + '_' + nmb + '.csv')
            bd_pd.to_csv(archivo)


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
        raise NotImplementedError
    else:
        raise ValueError(_('Formato de base de datos "{}" no reconocido.').format(ext))


class BD(object):
    """
    Una superclase para lectores de bases de datos.
    """

    def __init__(símismo, archivo):
        símismo.archivo = archivo

        if not os.path.isfile(archivo):
            raise FileNotFoundError(_('El archivo "{}" no existe.').format(archivo))

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
