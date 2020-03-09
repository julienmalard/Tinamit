class Modelo(object):
    simulador = SimulModelo

    def __init__(símismo, nombre, variables):
        símismo.nombre = nombre
        símismo.variables = variables

    def iniciar(símismo):
        return símismo.simulador(símismo)

    def simular(símismo):
        with símismo.iniciar() as sim:
            sim.correr()

    @property
    def unids(símismo):
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre
