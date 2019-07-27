import csv

import numpy as np
import xarray as xr

from tinamit.config import _
from tinamit.cositas import valid_nombre_arch, guardar_json
from .var import Variable


class ResultadosGrupo(dict):
    """
    Resultados de una simulación por grupo.
    """

    def __init__(símismo, nombre):
        símismo.nombre = nombre
        super().__init__()


class ResultadosSimul(object):
    """
    Resultados de una simulación.
    """

    def __init__(símismo, nombre, t, vars_interés):
        símismo.nombre = nombre
        símismo.t = t
        símismo.res_vars = {str(v): ResultadosVar(v, t) for v in vars_interés}
        # Para hacer: implementar xr.Dataset una vez se coordinen los nombres de dimensiones de variables

    def actualizar(símismo):
        for v in símismo:
            v.actualizar()

    def guardar(símismo, frmt='json', l_vars=None):
        """
        Guarda los resultados en un archivo.

        Parameters
        ----------
        frmt: str
            El formato deseado. Puede ser ``json`` o ``csv``.
        l_vars:
            La lista de variables de interés.
        """

        if l_vars is None:
            l_vars = list(símismo)
        elif isinstance(l_vars, (str, Variable)):
            l_vars = [l_vars]

        if frmt[0] != '.':
            frmt = '.' + frmt
        arch = valid_nombre_arch(símismo.nombre + frmt)

        if frmt == '.json':
            contenido = símismo.a_dic()
            guardar_json(contenido, arch=arch)

        elif frmt == '.csv':

            with open(arch, 'w', encoding='UTF-8', newline='') as a:
                escr = csv.writer(a)

                escr.writerow([_('fecha')] + símismo.t)
                for var in l_vars:
                    vals = símismo[var].values
                    if len(vals.shape) == 1:
                        escr.writerow([var] + vals.tolist())
                    else:
                        for í in range(vals.shape[1]):
                            escr.writerow(['{}[{}]'.format(var, í)] + vals[:, í].tolist())

        else:
            raise ValueError(_('Formato de resultados "{}" no reconocido.').format(frmt))

    def a_dic(símismo):
        """
        Convierte los resultados en diccionario.

        Returns
        -------
        dict
        """
        return {v: r.a_dic() for v, r in símismo.res_vars.items()}

    def variables(símismo):
        return [v.var for v in símismo]

    def poner_vals_t(símismo, valores):
        for vr, vl in valores.items():
            símismo[vr].poner_vals_t(vl)

    def __str__(símismo):
        return símismo.nombre

    def __iter__(símismo):
        for v in símismo.res_vars.values():
            yield v

    def __getitem__(símismo, itema):
        return símismo.res_vars[str(itema)]

    def __eq__(símismo, otro):
        return símismo.res_vars == otro.res_vars


class ResultadosVar(object):
    """
    Los resultados de un variable.
    """
    def __init__(símismo, var, t):
        símismo.var = var
        símismo.t = t

        dims = símismo.var.dims
        matr = np.zeros((len(t), *dims))
        símismo.vals = xr.DataArray(
            matr, coords={_('fecha'): símismo.t.eje()},
            dims=[_('fecha'), *('x_' + str(i) for i in range(len(dims)))]
        )

    def actualizar(símismo):
        símismo.vals[símismo.t.í // símismo.t.guardar_cada] = símismo.var.obt_val()

    def poner_vals_t(símismo, vals):
        símismo.vals[:] = vals.reshape(símismo.vals.shape)

    def a_dic(símismo):
        return símismo.vals.values

    def interpolar(símismo, fechas):
        eje_ant = símismo.vals[_('fecha')]
        nuevas_fechas = fechas.values[~np.isin(fechas.values, eje_ant.values)]
        vals = símismo.vals
        if nuevas_fechas.size:
            vals = vals.reindex(fecha=np.concatenate((eje_ant.values, nuevas_fechas)))
            vals = vals.sortby(_('fecha'))
            vals = vals.interpolate_na(_('fecha'))
        return vals.where(vals[_('fecha')].isin(fechas), drop=True)

    def __str__(símismo):
        return str(símismo.var)

    def __eq__(símismo, otro):
        return símismo.vals.equals(otro.vals)
