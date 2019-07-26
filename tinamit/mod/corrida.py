import itertools

from tinamit.config import _


class Corrida(object):
    def __init__(símismo, nombre, t, extern, vars_mod, vars_interés, clima):
        símismo.nombre = nombre
        símismo.t = t
        símismo.extern = extern

        símismo.variables = vars_mod

        símismo.clima = clima

        símismo.resultados = vars_mod.gen_res(
            nombre=nombre, t=t, vars_interés=vars_interés
        )

    def actualizar_res(símismo):
        if símismo.t.t_guardar():
            símismo.resultados.actualizar()

    def obt_extern_act(símismo, var=None):
        if símismo.extern:
            return {vr: vl.values[0] for vr, vl in símismo.extern.obt_vals(símismo.t, var=var).items()}

    def __str__(símismo):
        return símismo.nombre


class Rebanada(object):
    def __init__(símismo, n_pasos, resultados):
        símismo.n_pasos = n_pasos

        símismo.resultados = resultados


class PlantillaOpsSimulGrupo(object):
    """
    Clase pariente para especificaciones de corridas en grupo.
    """
    def __init__(símismo, **argsll):
        símismo.opciones = argsll

        for ll, v in símismo.opciones.items():
            if not isinstance(v, list):
                símismo.opciones[ll] = [v]

    def __iter__(símismo):
        raise NotImplementedError


class OpsSimulGrupoCombin(PlantillaOpsSimulGrupo):
    """
    Corridas en grupo que generan todas las combinaciones posibles de las opciones de simulación especificadas.
    """
    
    def __init__(símismo, t, extern=None, clima=None, vars_interés=None, nombre='Tinamït'):
        símismo.nombre = nombre
        símismo.vars_interés = vars_interés
        super().__init__(t=t, extern=extern, clima=clima)

    def __iter__(símismo):
        ops = itertools.product(*símismo.opciones.values())
        nmbs = ['t', 'extern', 'clima']
        for i, op in enumerate(ops):
            yield {
                **{n: o for n, o in zip(nmbs, op)},
                'nombre': '{}_{}'.format(símismo.nombre, str(i)),
                'vars_interés': símismo.vars_interés
            }


class OpsSimulGrupo(PlantillaOpsSimulGrupo):
    """
    Corridas en grupo sin combinaciones (las primeras opciones de cada parámetro se corrirán juntas en una
    simulación, seguidas por las segundas, etc.).
    """

    def __init__(símismo, t, extern=None, clima=None, vars_interés=None, nombre='Tinamït'):
        símismo.nombre = nombre
        símismo.vars_interés = vars_interés

        args = {
            't': t, 'extern': extern, 'clima': clima
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
                'vars_interés': símismo.vars_interés
            }
