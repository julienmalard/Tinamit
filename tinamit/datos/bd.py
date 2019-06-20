import os

import pandas as pd
import xarray as xr

from .fuente import Fuente, FuentePandas, FuenteDic, FuenteVarXarray, FuenteBaseXarray, FuenteCSV


class BD(object):
    def __init__(símismo, fuentes):
        símismo.fuentes = [fuentes] if isinstance(fuentes, Fuente) else fuentes
        símismo.vars_disp = list(set((v for f in símismo.fuentes for v in f.obt_vars())))

    def obt_vals(símismo, vars_interés, lugares=None, fechas=None, fuentes=None):
        fuentes_filtradas = símismo._filtrar_fuentes(fuentes)
        return xr.merge(
            (f.obt_vals(vars_interés=vars_interés, lugares=lugares, fechas=fechas) for f in fuentes_filtradas)
        )

    def _filtrar_fuentes(símismo, fuentes):
        fuentes = [fuentes] if isinstance(fuentes, (Fuente, str)) else fuentes
        fuentes = [str(f) for f in fuentes]
        for f in símismo.fuentes:
            if f.nombre in fuentes:
                yield f


def _gen_fuente(fnt, nombre=None, lugares=None, fechas=None):
    if isinstance(fnt, pd.DataFrame):
        return FuentePandas(nombre or 'pandas', fnt, lugares=lugares, fechas=fechas)

    elif isinstance(fnt, dict):
        return FuenteDic(nombre or 'dic', fnt, lugares=lugares, fechas=fechas)

    elif isinstance(fnt, xr.Dataset):
        return FuenteBaseXarray(nombre or 'xarray', fnt, lugares=lugares, fechas=fechas)

    elif isinstance(fnt, xr.DataArray):
        return FuenteVarXarray(nombre or 'xarray', fnt, lugares=lugares, fechas=fechas)

    elif isinstance(fnt, str):
        ext = os.path.splitext(fnt)[1]

        if ext == '.csv':
            return FuenteCSV(fnt, lugares=lugares, fechas=fechas)
        else:
            raise ValueError(_('Formato de base de datos "{}" no reconocido.').format(ext))
