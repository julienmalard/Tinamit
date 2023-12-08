import numpy as np
from tinamit.config import _


class ComportamientoVariable(object):
    def __init__(símismo, variables):
        símismo.variables = variables

    def gen_valores(símismo, modelo):
        raise NotImplementedError

    def verificar(símismo, res):
        raise NotImplementedError


class Igual(ComportamientoVariable):
    def __init__(símismo, var, valor):
        símismo.valor = valor
        símismo.var = var
        super().__init__([var])

    def gen_valores(símismo, modelo):
        return [{símismo.var: símismo.valor}]

    def verificar(símismo, res):
        res_var = res[símismo.var].vals
        vals = res_var.values
        dif = np.abs(vals - símismo.valor)
        if not np.all(dif == 0):
            raise ValueError(
                'Variable {var} no siempre igual a {valor}'.format(var=símismo.var, valor=símismo.valor)
            )


class Acerca(ComportamientoVariable):
    def __init__(símismo, var, valor, por=None):
        símismo.por = por
        símismo.valor = valor
        símismo.var = var
        super().__init__([var])

    def gen_valores(símismo, modelo):
        var = modelo.variables[símismo.var]
        if var.líms[0] > símismo.valor or var.líms[1] < símismo.valor:
            raise ValueError
        if símismo.por is None:
            por = 'arriba' if var.líms[0] == símismo.valor else 'debajo' if var.líms[1] == símismo.valor else 'ambos'
        raise NotImplementedError

    def verificar(símismo, res):
        res_var = res[símismo.var].vals
        vals = res_var.values
        dif = np.abs(vals - símismo.valor)
        rango = np.max(vals) - np.min(vals)
        n_pasos = len(res_var[_('fecha')])
        if not np.all(np.diff(dif[int(n_pasos * 0.9):], axis=0) <= 0):
            raise ValueError(
                'Variable {var} no se acerca consistamente a {valor}'.format(var=símismo.var, valor=símismo.valor)
            )
        if not dif[-1] <= rango * 0.01:
            raise ValueError('Variable {var} no se acerca a {valor}'.format(var=símismo.var, valor=símismo.valor))


class PruebaExtrema(object):
    def __init__(símismo, modelo, si, entonces):
        símismo.modelo = modelo
        símismo.si = si
        símismo.entonces = entonces

    def verificar(símismo, t=2500, **argsll):
        valores = símismo.si.gen_valores(símismo.modelo)
        for val in valores:
            res = símismo.modelo.simular(**argsll)
            símismo.entonces.verificar(res)
