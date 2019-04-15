import itertools

from tinamit.config import _

from .res import ResultadosSimul


class Corrida(object):
    def __init__(símismo, nombre, eje_tiempo, extern, vars_interés):
        símismo.nombre = nombre
        símismo.eje_tiempo = eje_tiempo
        símismo.extern = extern

        símismo.vars_interés = vars_interés
        símismo.resultados = ResultadosSimul(nombre=nombre, eje_tiempo=eje_tiempo, variables=vars_interés)

    def actualizar_res(símismo):
        if símismo.eje_tiempo.t_guardar():
            símismo.resultados.actualizar()


class OpsCorridaGrupo(object):
    def __init__(símismo, t, nombre_corrida, vals_inic, vals_extern, clima, vars_interés):
        símismo.nombre_corrida = nombre_corrida
        símismo.opciones = {
            't': t, 'vals_inic': vals_inic, 'vals_extern': vals_extern, 'clima': clima,
            'vars_interés': vars_interés
        }
        for ll, v in símismo.opciones:
            if not isinstance(v, list):
                símismo.opciones[ll] = [v]

    def __iter__(símismo):
        ops = itertools.product(símismo.opciones.values())
        nmbs = ['t', 'vals_inic', 'vals_extern', 'clima']
        for i, op in enumerate(ops):
            yield {
                **{n: o for n, o in zip(nmbs, op)},
                'nombre_corrida': '{}_{}'.format(símismo.nombre_corrida, str(i))
            }


class OpsCorridaGrupoSenc(OpsCorridaGrupo):

    def __init__(símismo, t, nombre_corrida, vals_inic, vals_extern, clima, vars_interés):
        super().__init__(t, nombre_corrida, vals_inic, vals_extern, clima, vars_interés)
        tmñs = {len(o) for o in símismo.opciones if len(o) != 1}

        if len(tmñs) > 1:
            raise ValueError(_('Todas las opciones deben tener el mismo número de valores.'))
        elif not tmñs:
            símismo.tmñ_ops = 1
        else:
            símismo.tmñ_ops = list(tmñs)[0]

    def __iter__(símismo):
        for i in range(símismo.tmñ_ops):
            yield {
                **{n: op[i] for n, op in símismo.opciones.items()},
                'nombre_corrida': '{}_{}'.format(símismo.nombre_corrida, str(i))
            }
