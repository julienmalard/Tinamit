from abc import ABC, abstractmethod


class Modelo(ABC):
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
    @abstractmethod
    def unids(símismo):
        pass

    def __str__(símismo):
        return símismo.nombre
