from ..mod import ResultadosSimul


class ResultadosConectado(ResultadosSimul):
    def __init__(símismo, nombre, t, modelos, vars_interés):
        super().__init__(nombre, t, vars_interés=[])
        símismo.res_vars = {
            str(m): m.variables.gen_res(nombre, t, [v for v in vars_interés if v in m.variables]) for m in modelos
        }

    def a_dic(símismo):
        return {m: v.a_dic() for m, v in símismo.res_vars.items()}

    def __iter__(símismo):
        for m in símismo.res_vars.values():
            for v in m:
                yield v
