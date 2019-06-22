import csv
import datetime
import os

import numpy as np
import pandas as pd
import xarray as xr

from tinamit.config import _
from tinamit.cositas import detectar_codif
from எண்ணிக்கை import எண்ணுக்கு as எ


class Fuente(object):

    def __init__(símismo, nombre, variables, lugares=None, fechas=None):
        símismo.nombre = nombre
        símismo.lugares = lugares
        símismo.variables = variables

        símismo._equiv_nombres = {}

        try:
            símismo.fechas = pd.to_datetime(fechas)
        except ValueError:
            símismo.fechas = fechas

    def obt_vals(símismo, vars_interés, lugares=None, fechas=None):

        coords = símismo._gen_coords()
        if isinstance(vars_interés, str):
            vals = xr.DataArray(
                símismo._vec_var(símismo._resolver_nombre(vars_interés)),
                coords=coords, dims='n', name=vars_interés
            )
        else:
            vals = xr.Dataset(
                {vr: ('n', símismo._vec_var(símismo._resolver_nombre(vr))) for vr in vars_interés},
                coords=coords
            )

        return símismo._filtrar_lugares(símismo._filtrar_fechas(vals, fechas), lugares)

    def obt_lugar(símismo):
        if isinstance(símismo.lugares, str):
            try:
                return símismo._vec_var(símismo.lugares, tx=True)
            except KeyError:
                pass
        return símismo.lugares

    def obt_fecha(símismo):
        if isinstance(símismo.fechas, str):
            fechas = símismo._vec_var(símismo.fechas, tx=True)
        else:
            fechas = símismo.fechas
        return pd.to_datetime(fechas, infer_datetime_format=True)

    def equiv_nombre(símismo, var, equiv):
        símismo._equiv_nombres[equiv] = var

    def _resolver_nombre(símismo, var):
        try:
            símismo._equiv_nombres[var]
        except KeyError:
            return var

    def _gen_coords(símismo):
        coords = {}
        lugar = símismo.obt_lugar()
        fecha = símismo.obt_fecha()
        if isinstance(lugar, (np.ndarray, pd.Series)):
            coords[_('lugar')] = ('n', lugar)
        else:
            coords[_('lugar')] = lugar
        if isinstance(fecha, (np.ndarray, pd.Series, pd.DatetimeIndex)):
            coords[_('tiempo')] = ('n', fecha)
        else:
            coords[_('tiempo')] = fecha

        return coords

    def _vec_var(símismo, var, tx=False):
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
        fechas = vals[_('tiempo')]
        if isinstance(criteria, tuple) and len(criteria) == 2:
            cond = np.logical_and(np.less_equal(fechas, criteria[1]), np.greater_equal(fechas, criteria[0]))
        else:
            criteria = [criteria] if isinstance(criteria, pd.Timestamp) else criteria
            cond = fechas.isin(criteria)
        return vals.where(cond, drop=True)

    def __str__(símismo):
        return símismo.nombre


class FuenteCSV(Fuente):
    def __init__(símismo, archivo, nombre=None, lugares=None, fechas=None, cód_vacío=None):
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
                if tx:
                    val = f[var].strip()

                else:
                    val = எ(f[var].strip()) if f[var].strip() not in símismo.cód_vacío else np.nan

                l_datos.append(val)

        return np.array(l_datos)


class FuenteDic(Fuente):

    def __init__(símismo, dic, nombre, lugares=None, fechas=None):
        símismo.dic = dic
        super().__init__(nombre, variables=list(símismo.dic), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return np.array(símismo.dic[var])


class FuenteVarXarray(Fuente):

    def __init__(símismo, obj, nombre, lugares=None, fechas=None):
        símismo.obj = obj
        super().__init__(nombre, variables=[símismo.obj.name], lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj


class FuenteBaseXarray(Fuente):

    def __init__(símismo, obj, nombre, lugares=None, fechas=None):
        símismo.obj = obj
        super().__init__(nombre, variables=list(símismo.obj.data_vars), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj[var]


class FuentePandas(Fuente):
    def __init__(símismo, obj, nombre, lugares=None, fechas=None):
        símismo.obj = obj
        super().__init__(nombre, variables=list(símismo.obj), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj[var]
