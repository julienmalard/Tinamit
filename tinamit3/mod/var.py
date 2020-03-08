class Variable(object):
    def __init__(símismo, nombre, unids):
        pass


class VariablesModelo(object):
    def __init__(símismo, variables):
        símismo.variables = {str(var): var for var in variables}
        duplicados = [x for x in set(símismo.variables) if list(símismo.variables).count(x) > 1]
        if duplicados:
            raise ValueError('Variables duplicados: {}'.format(', '.join(duplicados)))

    def __getitem__(símismo, itema):
        return símismo.variables[itema]


class ValorVariable(object):
    pass
