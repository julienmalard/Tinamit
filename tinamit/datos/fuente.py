import csv
import datetime as ft
import os

import numpy as np
import pandas as pd
import xarray as xr
from tinamit.config import _
from tinamit.cositas import detectar_codif
from எண்ணிக்கை import எண்ணுக்கு as எ


class Fuente(object):
    """
    La clase pariente para fuentes de datos.
    """

    def __init__(símismo, nombre, variables, lugares=None, fechas=None):
        símismo.nombre = nombre

        símismo.variables = [vr for vr in variables if vr not in [lugares, fechas]]

        símismo._equiv_nombres = {}

        if fechas is None:
            fechas = pd.NaT
        símismo.n_obs = símismo._vec_var(símismo.variables[0], tx=True).size

        símismo.lugares = símismo._obt_lugar(lugares)
        símismo.fechas = símismo._obt_fecha(fechas)

    def obt_vals(símismo, vars_interés, lugares=None, fechas=None):
        vars_interés = vars_interés or símismo.variables

        coords = {_('lugar'): ('n', símismo.lugares), _('fecha'): ('n', símismo.fechas)}
        if isinstance(vars_interés, str):
            vals = xr.DataArray(
                símismo._vec_var(símismo._resolver_nombre(vars_interés)),
                coords=coords, dims='n', name=vars_interés
            )
        else:
            vals = xr.Dataset(
                {vr: ('n', símismo._vec_var(símismo._resolver_nombre(vr)))
                 for vr in vars_interés if vr in símismo.variables
                 },
                coords=coords
            )
        vals = vals.set_index(n=['lugar', 'fecha'])
        return símismo._filtrar_lugares(símismo._filtrar_fechas(vals, fechas), lugares)

    def _obt_lugar(símismo, lugares):
        lugares = lugares or ''
        if isinstance(lugares, str):
            try:
                lugares = símismo._vec_var(lugares, tx=True)
            except KeyError:
                return np.full(símismo.n_obs, lugares)

        return lugares

    def _obt_fecha(símismo, fechas):
        if isinstance(fechas, str):
            try:
                fechas = símismo._vec_var(fechas, tx=True)
            except KeyError:
                pass
            fechas = pd.to_datetime(fechas)
        if isinstance(fechas, pd.Timestamp):
            fechas = pd.to_datetime(np.full(símismo.n_obs, fechas.to_datetime64()))
        elif isinstance(fechas, (ft.date, ft.datetime)):
            fechas = pd.to_datetime(np.full(símismo.n_obs, fechas).astype(ft.datetime))

        return fechas

    def equiv_nombre(símismo, var, equiv):
        símismo._equiv_nombres[equiv] = var

    def _resolver_nombre(símismo, var):
        try:
            símismo._equiv_nombres[var]
        except KeyError:
            return var

    def _vec_var(símismo, var, tx=False):
        """
        Devuelve un vector de los valores de un variable.

        Parameters
        ----------
        var: str
            El nombre del variable.
        tx: bool
            Si quieres formato de texto o numérico.

        Returns
        -------
        np.ndarray
        """
        raise NotImplementedError

    @staticmethod
    def _filtrar_lugares(vals, criteria):
        if criteria is None:
            return vals
        criteria = [criteria] if isinstance(criteria, str) else criteria
        return vals.where(vals[_('lugar')].isin(criteria), drop=True)

    @staticmethod
    def _filtrar_fechas(vals, criteria):
        if criteria is None:
            return vals
        criteria = pd.to_datetime(criteria)
        if isinstance(criteria, pd.Timestamp):
            criteria = criteria.to_datetime64()
        fechas = vals[_('fecha')]
        if isinstance(criteria, tuple) and len(criteria) == 2:
            cond = np.logical_and(np.less_equal(fechas, criteria[1]), np.greater_equal(fechas, criteria[0]))
        else:
            cond = fechas.isin(criteria)
        return vals.where(cond, drop=True)

    def __str__(símismo):
        return símismo.nombre


class FuenteCSV(Fuente):
    """
    Fuente para archivos ``.csv``.
    """
    def __init__(símismo, archivo, nombre=None, lugares=None, fechas=None, cód_vacío=None):
        """

        Parameters
        ----------
        archivo: str
            El archivo con los datos.
        nombre: str
            El nombre de la fuente.
        lugares: str or np.ndarray or list
            Los lugares que corresponden a los datos. Puede se nombre de una columna en el csv, el nombre de un
            lugar de cual vienen todos los datos, o una lista de los lugares.
        fechas: str or np.ndarray or list or datetime.datetime
            Las fechas de los datos.
        cód_vacío:
            Código para identificar variables que faltan. ``NA`` y ``NaN`` ya están reconocidos.
        """
        nombre = nombre or os.path.splitext(os.path.split(archivo)[1])[0]
        símismo.archivo = archivo
        símismo.codif = detectar_codif(archivo, máx_líneas=1)

        cód_vacío = cód_vacío or ['na', 'NA', 'NaN', 'nan', 'NAN', '']
        símismo.cód_vacío = [cód_vacío] if isinstance(cód_vacío, (int, float, str)) else cód_vacío

        super().__init__(nombre, variables=símismo.obt_vars(), lugares=lugares, fechas=fechas)

    def obt_vars(símismo):
        with open(símismo.archivo, encoding=símismo.codif) as d:
            lector = csv.reader(d)

            nombres_cols = next(lector)

        return nombres_cols

    def _vec_var(símismo, var, tx=False):
        l_datos = []
        with open(símismo.archivo, encoding=símismo.codif) as d:
            lector = csv.DictReader(d)

            for n_f, f in enumerate(lector):
                val = f[var].strip()
                if not tx:
                    if val in símismo.cód_vacío:
                        val = np.nan
                    else:
                        try:
                            val = எ(val)
                        except ValueError:
                            val = float(val)
                l_datos.append(val)

        return np.array(l_datos)


class FuenteDic(Fuente):
    """
    Fuente de datos en forma de diccionario.
    """

    def __init__(símismo, dic, nombre, lugares=None, fechas=None):
        """

        Parameters
        ----------
        dic: dict
            El diccionario con los datos.
        nombre: str
            El nombre de la fuente.
        lugares: str or np.ndarray or list
            Los lugares que corresponden a los datos. Puede se nombre de una llave en el dictionario, el nombre de un
            lugar de cual vienen todos los datos, o una lista de los lugares.
        fechas: str or np.ndarray or list or datetime.datetime
            Las fechas de los datos.
        """
        símismo.dic = dic
        super().__init__(nombre, variables=list(símismo.dic), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return np.array(símismo.dic[var])


class FuenteVarXarray(Fuente):
    """
    Fuente para datos en formato de ``DataArray`` de ``xarray``.
    """

    def __init__(símismo, obj, nombre, lugares=None, fechas=None):
        """

        Parameters
        ----------
        obj: xarray.DataArray
            Los datos
        nombre: str
            El nombre de la fuente.
        lugares: str or np.ndarray or list
            Los lugares que corresponden a los datos. Puede se nombre de una columna en el ``DataArray``, el nombre de
            un lugar de cual vienen todos los datos, o una lista de los lugares.
        fechas: str or np.ndarray or list or datetime.datetime
            Las fechas de los datos.
        """
        símismo.obj = obj
        super().__init__(nombre, variables=[símismo.obj.name], lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj


class FuenteBaseXarray(Fuente):
    """
    Fuente para datos en formato de ``Dataset`` de ``xarray``.
    """
    def __init__(símismo, obj, nombre, lugares=None, fechas=None):
        """

        Parameters
        ----------
        obj: xarray.Dataset
            Los datos
        nombre: str
            El nombre de la fuente.
        lugares: str or np.ndarray or list
            Los lugares que corresponden a los datos. Puede se nombre de una columna en el ``Dataset``, el nombre de un
            lugar de cual vienen todos los datos, o una lista de los lugares.
        fechas: str or np.ndarray or list or datetime.datetime
            Las fechas de los datos.
        """
        símismo.obj = obj
        super().__init__(nombre, variables=list(símismo.obj.data_vars), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj[var]


class FuentePandas(Fuente):
    """
    Fuente para datos en formato de ``DataFrame`` de ``xarray``.
    """
    def __init__(símismo, obj, nombre, lugares=None, fechas=None):
        """

        Parameters
        ----------
        obj: pd.DataFrame
            Los datos
        nombre: str
            El nombre de la fuente.
        lugares: str or np.ndarray or list
            Los lugares que corresponden a los datos. Puede se nombre de una columna en el ``Dataset``, el nombre de un
            lugar de cual vienen todos los datos, o una lista de los lugares.
        fechas: str or np.ndarray or list or datetime.datetime
            Las fechas de los datos.
        """
        símismo.obj = obj
        super().__init__(nombre, variables=list(símismo.obj), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj[var]
