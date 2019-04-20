import numpy as np

from tinamit.envolt.bf import ModeloBloques, ModeloDeterminado, ModeloIndeterminado, VariablesModDeter, VarCiclo, \
    VariablesModImpaciente, VarBloque
from tinamit.mod import Variable


class EjBloques(ModeloBloques):

    def __init__(símismo, tmñ_bloques, unid_tiempo='días'):
        símismo.unid_tiempo = unid_tiempo

        super().__init__(tmñ_bloques=tmñ_bloques, variables=símismo._gen_vars())

    @staticmethod
    def _gen_vars():
        return VariablesModBloque([
            VarCiclo('ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            VarBloque('bloque', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('paso', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('i_en_ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('ingreso', unid=None, ingr=True, egr=False, líms=(0, None))
        ])

    def cerrar(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def avanzar_modelo(símismo, n_ciclos):
        pass



class EjDeterminado(ModeloDeterminado):

    def __init__(símismo, tmñ_ciclo, unid_tiempo='días'):
        símismo.unid_tiempo = unid_tiempo

        super().__init__(tmñ_ciclo=tmñ_ciclo, variables=símismo._gen_vars())

    @staticmethod
    def _gen_vars():
        return VariablesModDeter([
            VarCiclo('ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('paso', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('i_en_ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('ingreso', unid=None, ingr=True, egr=False, líms=(0, None))
        ])

    def cerrar(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def avanzar_modelo(símismo, n_ciclos):
        símismo.variables['paso'] +=


class EjIndeterminado(ModeloIndeterminado):

    def __init__(símismo, rango_n, unid_tiempo='días'):
        símismo.rango_n = rango_n
        símismo.unid_tiempo = unid_tiempo
        símismo.n = np.random.randint(*rango_n)

        super().__init__(variables=símismo._gen_vars())

    @staticmethod
    def _gen_vars():
        return VariablesModImpaciente([
            Variable('ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('paso', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('ingreso', unid=None, ingr=True, egr=False, líms=(0, None))
        ])

    def cerrar(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def mandar_modelo(símismo):
        símismo.n = np.random.randint(*símismo.rango_n)
        return símismo.n
