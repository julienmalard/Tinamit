import itertools

from tinamit.config import _
from .res import ResultadosSimul


class Corrida(object):
    def __init__(símismo, nombre, t, extern, vars_mod, vars_interés):
        símismo.nombre = nombre
        símismo.t = t
        símismo.extern = extern

        símismo.variables = vars_mod.vars_simul()
        símismo.vars_interés = vars_interés

        símismo.resultados = ResultadosSimul(
            nombre=nombre, t=t, variables=[v for v in símismo.variables if v.base in vars_interés]
        )

    def actualizar_res(símismo):
        if símismo.t.t_guardar():
            símismo.resultados.actualizar()


class PlantillaOpsCorridaGrupo(object):
    def __init__(símismo, **argsll):
        símismo.opciones = argsll

        for ll, v in símismo.opciones.items():
            if not isinstance(v, list):
                símismo.opciones[ll] = [v]

    def __iter__(símismo):
        raise NotImplementedError


class OpsCorridaGrupoCombin(PlantillaOpsCorridaGrupo):
    def __init__(símismo, t, vals_extern=None, clima=None, vars_interés=None, nombre='Tinamït'):
        símismo.nombre = nombre
        super().__init__(t=t, vals_extern=vals_extern, clima=clima, vars_interés=vars_interés)

    def __iter__(símismo):
        ops = itertools.product(*símismo.opciones.values())
        nmbs = ['t', 'vals_extern', 'clima']
        for i, op in enumerate(ops):
            yield {
                **{n: o for n, o in zip(nmbs, op)},
                'nombre': '{}_{}'.format(símismo.nombre, str(i))
            }


class OpsCorridaGrupo(PlantillaOpsCorridaGrupo):

    def __init__(símismo, t, vals_extern=None, clima=None, vars_interés=None, nombre='Tinamït'):
        símismo.nombre = nombre

        args = {
            't': t, 'vals_extern': vals_extern, 'clima': clima, 'vars_interés': vars_interés
        }
        if not isinstance(nombre, str):
            args['nombre'] = nombre

        super().__init__(**args)

        tmñs = {len(o) for o in símismo.opciones.values() if len(o) != 1}

        if len(tmñs) > 1:
            raise ValueError(_('Todas las opciones deben tener el mismo número de valores.'))
        elif not tmñs:
            símismo.tmñ_ops = 1
        else:
            símismo.tmñ_ops = list(tmñs)[0]

        if 'nombre' not in símismo.opciones:
            símismo.opciones['nombre'] = ['{}_{}'.format(nombre, str(i)) for i in range(símismo.tmñ_ops)]

    def __iter__(símismo):
        for i in range(símismo.tmñ_ops):
            yield {
                **{n: op[i] if len(op) > 1 else op[0] for n, op in símismo.opciones.items()},
            }
