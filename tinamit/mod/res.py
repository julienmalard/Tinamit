class ResultadosSimul(object):
    pass


class ResultadosModelo(object):
    def __init__(símismo, modelo):
        símismo.modelo = modelo
        símismo._res_vars = {str(v): ResultadosVar(v) for v in modelo.variables}

    def __str__(símismo):
        return str(símismo.modelo)

    def __iter__(símismo):
        for v in símismo._res_vars.values():
            yield v


class ResultadosVar(object):
    def __init__(símismo, var, ):
        símismo.var = var

    def __str__(símismo):
        return str(símismo.var)
