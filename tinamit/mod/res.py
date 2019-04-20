import csv

import numpy as np
import xarray as xr

from tinamit.config import _
from tinamit.cositas import valid_nombre_arch, guardar_json
from .var import Variable


class ResultadosGrupo(dict):

    def __init__(símismo, nombre):
        símismo.nombre = nombre
        super().__init__()


class ResultadosSimul(object):

    def __init__(símismo, nombre, t, variables):
        símismo.nombre = nombre
        símismo.t = t
        símismo.res_vars = {str(v): ResultadosVar(v, t) for v in variables}

    def actualizar(símismo):
        for v in símismo:
            v.actualizar()

    def guardar(símismo, frmt='json', l_vars=None):

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

                escr.writerow([_('tiempo')] + símismo.t)
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
        return {v: r.a_dic() for v, r in símismo.res_vars.items()}

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
    def __init__(símismo, var, t):
        símismo.var = var
        símismo.t = t

        dims = símismo.var.dims
        matr = np.zeros((len(t), *dims))
        símismo.vals = xr.DataArray(
            matr, coords={_('tiempo'): símismo.t.eje()},
            dims=[_('tiempo'), *('x_' + str(i) for i in range(len(dims)))]
        )

    def actualizar(símismo):
        símismo.vals[símismo.t.í // símismo.t.guardar_cada] = símismo.var.obt_val()

    def __str__(símismo):
        return str(símismo.var)

    def __eq__(símismo, otro):
        return símismo.vals.equals(otro.vals)
