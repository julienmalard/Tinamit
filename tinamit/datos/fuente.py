import csv
import datetime
import os

import numpy as np
import xarray as xr
from tinamit.config import _
from tinamit.cositas import detectar_codif, _gen_fecha

from எண்ணிக்கை import எண்ணுக்கு as எ


class Fuente(object):

    def __init__(símismo, nombre, vars_disp, lugares=None, fechas=None):
        símismo.nombre = nombre
        símismo.lugares = lugares
        símismo.vars_disp = vars_disp

        símismo._equiv_nombres = {}

        try:
            símismo.fechas = _gen_fecha(fechas)
        except ValueError:
            símismo.fechas = fechas

    def obt_vals(símismo, vars_interés, lugares=None, fechas=None):

        coords = {_('lugar'): ('n', símismo.obt_lugar()), _('tiempo'): ('n', símismo.obt_fecha())}
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

        if lugares is not None:
            vals = vals[vals[_('lugar')] in lugares]
        if fechas is not None:
            vals = vals[vals[_('tiempo')] in fechas]

        return vals[np.logical_and(
            símismo._filtrar_fechas(vals[_('tiempo')], fechas),
            símismo._filtrar_lugares(vals['lugar'], lugares)
        )]

    def obt_lugar(símismo):
        if isinstance(símismo.lugares, str):
            return símismo._vec_var(símismo.lugares, tx=True)
        return símismo.lugares

    def obt_fecha(símismo):
        if isinstance(símismo.fechas, str):
            return símismo._vec_var(símismo.fechas, tx=True).astype('datetime64')
        return símismo.fechas

    def equiv_nombre(símismo, var, equiv):
        símismo._equiv_nombres[equiv] = var

    def _resolver_nombre(símismo, var):
        try:
            símismo._equiv_nombres[var]
        except KeyError:
            return var

    def _vec_var(símismo, var, tx=False):
        raise NotImplementedError

    @staticmethod
    def _filtrar_lugares(lugares, criteria):
        if criteria is None:
            return lugares

        criteria = [criteria] if isinstance(criteria, str) else criteria
        return np.isin(lugares, criteria)

    @staticmethod
    def _filtrar_fechas(fechas, criteria):
        if criteria is None:
            return fechas
        elif isinstance(criteria, tuple) and len(criteria) == 2:
            return np.logical_and(np.less_equal(fechas, criteria[1]), np.greater_equal(fechas, criteria[0]))

        criteria = [criteria] if isinstance(criteria, datetime.datetime) else criteria
        return np.isin(fechas, criteria)

    def __str__(símismo):
        return símismo.nombre


class FuenteCSV(Fuente):
    def __init__(símismo, archivo, nombre=None, lugares=None, fechas=None, cód_vacío=None):
        nombre = nombre or os.path.splitext(os.path.split(archivo)[1])[0]
        símismo.archivo = archivo
        símismo.codif = detectar_codif(archivo, máx_líneas=1)

        cód_vacío = cód_vacío or ['na', 'NA', 'NaN', 'nan', 'NAN', '']
        símismo.cód_vacío = [cód_vacío] if isinstance(cód_vacío, (int, float, str)) else cód_vacío

        super().__init__(nombre, vars_disp=símismo.obt_vars(), lugares=lugares, fechas=fechas)

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
                    val = f[var]

                else:
                    val = எ(f[var].strip()) if f[var].strip() not in símismo.cód_vacío else np.nan

                l_datos.append(val)

        return np.array(l_datos)


class FuenteDic(Fuente):

    def __init__(símismo, dic, nombre, lugares=None, fechas=None):
        símismo.dic = dic
        super().__init__(nombre, vars_disp=list(símismo.dic), lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return np.array(símismo.dic[var])


class FuenteVarXarray(Fuente):

    def __init__(símismo, nombre, obj, lugares=None, fechas=None):
        símismo.obj = obj
        super().__init__(nombre, vars_disp=[símismo.obj.name], lugares=lugares, fechas=fechas)

    def _vec_var(símismo, var, tx=False):
        return símismo.obj


class FuenteBaseXarray(Fuente):

    def __init__(símismo, nombre, obj, lugares=None, fechas=None):
        super().__init__(nombre, vars_disp=list(símismo.obj.data_vars), lugares=lugares, fechas=fechas)
        símismo.obj = obj

    def _vec_var(símismo, var, tx=False):
        return símismo.obj[var]


class FuentePandas(Fuente):
    def __init__(símismo, nombre, obj, lugares=None, fechas=None):
        super().__init__(nombre, vars_disp=list(símismo.obj), lugares=lugares, fechas=fechas)
        símismo.obj = obj

    def _vec_var(símismo, var, tx=False):
        return símismo.obj[var]
