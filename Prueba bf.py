import random


class Modelo(object):
    def __init__(símismo):
        símismo.variables = {'var1': {'var': 3, 'unidades': 'kg/ha'}, 'var2': {'var': 2, 'unidades': 'cm/día'}}
        símismo.unidades_tiempo = 'Meses'

    def ejec(símismo):
        pass

    def incr(símismo, paso):
        símismo.variables['var1']['var'] += random.random()*símismo.variables['var2']['var'] * paso
         += random.random()*2 * paso

    def actualizar(símismo, var, valor):
        pass
