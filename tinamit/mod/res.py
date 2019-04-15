import csv

import numpy as np
from tinamit.config import _
from tinamit.cositas import valid_nombre_arch, guardar_json

from .var import Variable


class ResultadosGrupo(object):
    def __init__(símismo):
        símismo._corridas = {}

    def __getitem__(símismo, itema):
        return símismo._corridas[itema]

    def __setitem__(símismo, llave, valor):
        símismo._corridas[llave] = valor


class ResultadosSimul(object):

    def __init__(símismo, nombre, eje_tiempo, variables):
        símismo.nombre = nombre
        símismo.eje_tiempo = eje_tiempo
        símismo._res_vars = {str(v): ResultadosVar(v, eje_tiempo) for v in variables}

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

                escr.writerow([_('tiempo')] + símismo.eje_tiempo)
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
        return {v: r.a_dic() for v, r in símismo._res_vars.items()}

    def __str__(símismo):
        return str(símismo.nombre)

    def __iter__(símismo):
        for v in símismo._res_vars.values():
            yield v

    def __getitem__(símismo, itema):
        return símismo._res_vars[str(itema)]


class ResultadosVar(object):
    def __init__(símismo, var, eje_tiempo):
        símismo.var = var
        símismo.eje_tiempo = eje_tiempo

        símismo._vals = np.zeros((len(eje_tiempo), *símismo.var.dims))

    def actualizar(símismo):
        símismo._vals[símismo.eje_tiempo.í] = símismo.var.obt_val()

    def __str__(símismo):
        return str(símismo.var)
