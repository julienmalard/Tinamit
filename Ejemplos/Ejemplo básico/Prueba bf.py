import random
from Biofísico import ClaseModeloBF


class Modelo(ClaseModeloBF):
    def __init__(símismo):
        super().__init__()

        símismo.variables = {'var1': {'var': 3,
                                      'unidades': 'kg/ha'
                                      },
                             'var2': {'var': 2,
                                      'unidades': 'cm/día'
                                      }
                             }

        símismo.unidades_tiempo = 'Meses'

    def ejec(símismo):
        pass

    def incr(símismo, paso):
        símismo.variables['var1']['var'] += random.random()*símismo.variables['var2']['var'] * paso
