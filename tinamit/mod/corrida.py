import itertools
from tinamit.config import _

class Corrida(object):
    def __init__(símismo, nombre, eje_tiempo, extern):
        símismo.nombre = nombre
        símismo.eje_tiempo = eje_tiempo
        símismo.extern = extern


class OpsCorridaGrupo(object):
    def __init__(símismo, t, nombre_corrida, vals_inic, vals_extern, clima, vars_interés, paralelo=None):
        símismo.nombre_corrida = nombre_corrida
        símismo.opciones = {
            't': t, 'vals_inic': vals_inic, 'vals_extern': vals_extern, 'clima': clima,
            'vars_interés': vars_interés
        }
        for ll, v in símismo.opciones:
            if not isinstance(v, list):
                símismo.opciones[ll] = [v]

        símismo.paralelo = paralelo

    def __iter__(símismo):
        ops = itertools.product(símismo.opciones.values())
        nmbs = ['t', 'vals_inic', 'vals_extern', 'clima']
        for op in ops:
            yield {n: o for n, o in zip(nmbs, op)}


class OpsCorridaGrupoSenc(OpsCorridaGrupo):

    def __init__(símismo, t, nombre_corrida, vals_inic, vals_extern, clima, vars_interés, paralelo=None):
        super().__init__(t, nombre_corrida, vals_inic, vals_extern, clima, vars_interés, paralelo)
        símismo.tmñ_ops = len({len(val) for val in símismo.opciones.values() if len(val) != 1})  # para hacer
        if not len({len(val) for val in símismo.opciones.values() if len(val) != 1}) == 1:
            raise ValueError(_('Todas las opciones deben tener el mismo número de valores.'))

    def __iter__(símismo):
        for i in range(símismo.tmñ_ops):
            yield {n: op[i] for n, op in símismo.opciones.items()}
