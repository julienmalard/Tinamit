import os

import numpy as np
import pandas as pd
import xarray as xr

from tinamit.config import _
from .fuente import FuentePandas, FuenteDic, FuenteVarXarray, FuenteBaseXarray, FuenteCSV


class BD(object):
    def __init__(símismo, fuentes):
        fuentes = [fuentes] if not isinstance(fuentes, (list, tuple)) else fuentes
        símismo.fuentes = [_gen_fuente(f) for f in fuentes]
        símismo.variables = list(set((v for f in símismo.fuentes for v in f.variables)))

    def obt_vals(símismo, vars_interés=None, lugares=None, fechas=None):
        """

        Parameters
        ----------
        vars_interés
        lugares
        fechas

        Returns
        -------
        xr.DataArray, xr.Dataset
        """

        return xr.concat(
            (f.obt_vals(vars_interés=vars_interés, lugares=lugares, fechas=fechas) for f in símismo.fuentes), 'n'
        )

    def interpolar(símismo, vars_interés, fechas, lugares=None, extrap=False):
        datos = símismo.obt_vals(vars_interés=vars_interés, lugares=lugares, fechas=None)
        fechas = pd.to_datetime(fechas)
        if isinstance(fechas, pd.Timestamp):
            fechas = pd.DatetimeIndex([fechas])

        lugares_únicos = set(datos[_('lugar')].values.tolist())
        bds_lugares = {
            lg: datos.where(datos[_('lugar')].isnull() if lg is None else datos[_('lugar')] == lg, drop=True)
            for lg in lugares_únicos
        }

        # Para cada lugar...
        for lg, bd_lg in bds_lugares.items():

            # Las nuevas fechas de interés que hay que a la base de datos
            nuevas_fechas = [x for x in pd.DatetimeIndex(fechas) if not (bd_lg[_('tiempo')] == x.to_datetime64()).any()]

            if isinstance(bd_lg, xr.Dataset):
                vacíos = xr.Dataset(
                    data_vars={x: ('n', np.full(len(nuevas_fechas), np.nan)) for x in bd_lg.data_vars},
                    coords=dict(tiempo=('n', nuevas_fechas),
                                **{_('lugar'): ('n', [lg] * len(nuevas_fechas))}
                                )
                )
            else:
                vacíos = xr.DataArray(
                    data=np.full(len(nuevas_fechas), np.nan),
                    coords=dict(tiempo=('n', nuevas_fechas), **{_('lugar'): ('n', [lg] * len(nuevas_fechas))}),
                    dims='n', name=bd_lg.name
                )
            if len(vacíos):
                bd_lg = xr.concat((bd_lg, vacíos), 'n')
            bd_lg = bd_lg.sortby(_('tiempo')).interpolate_na('n', use_coordinate=_('tiempo'))

            if extrap:
                # Si quedaron combinaciones de variables y de fechas para las cuales no pudimos interpolar porque
                # las fechas que faltaban se encontraban afuera de los límites de los datos disponibles,
                # simplemente copiar el último valor disponible.
                todavía_faltan = [x for x in bd_lg.data_vars if bd_lg.isnull().any()[x]]
                for v in todavía_faltan:
                    existen = np.where(bd_lg[v].notnull())[0]
                    if len(existen):
                        primero = existen[0]
                        último = existen[-1]
                        bd_lg[v][:primero] = bd_lg[v][primero]
                        bd_lg[v][último + 1:] = bd_lg[v][último]
            bds_lugares[lg] = bd_lg

        return xr.concat(bds_lugares.values(), 'n').sortby(_('lugar')).sortby(_('tiempo'))


def _gen_fuente(fnt, nombre=None, lugares=None, fechas=None):
    if isinstance(fnt, pd.DataFrame):
        return FuentePandas(fnt, nombre or 'pandas', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, dict):
        return FuenteDic(fnt, nombre or 'dic', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, xr.Dataset):
        return FuenteBaseXarray(fnt, nombre or 'xarray', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, xr.DataArray):
        return FuenteVarXarray(fnt, nombre or 'xarray', lugares=lugares, fechas=fechas)

    elif isinstance(fnt, str):
        ext = os.path.splitext(fnt)[1]

        if ext == '.csv':
            return FuenteCSV(fnt, lugares=lugares, fechas=fechas)
        else:
            raise ValueError(_('Formato de base de datos "{}" no reconocido.').format(ext))

    return fnt
