from abc import ABC


class SimulModelo(ABC):
    def __init__(símismo, modelo, t):
        símismo.modelo = modelo
        símismo.t = t

    def incrementar(símismo, rbnd):
        pass

    def cerrar(símismo):
        pass

    def __enter__(símismo):
        return símismo

    def __exit__(símismo, exc_type, exc_val, exc_tb):
        símismo.cerrar()

    def __str__(símismo):
        return str(símismo.modelo)
