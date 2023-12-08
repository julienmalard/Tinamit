import numpy as np

from tinamit.envolt.bf import ModeloBloques, ModeloDeterminado, ModeloIndeterminado, VariablesModDeter, \
    VariablesModIndeterminado, VarBloque, VarPasoDeter, VariablesModBloques, VarPasoIndeter
from tinamit.mod import Variable


class EjDeterminado(ModeloDeterminado):

    def __init__(símismo, tmñ_ciclo, unid_tiempo='días'):
        símismo.unid_tiempo = unid_tiempo

        super().__init__(tmñ_ciclo=tmñ_ciclo, variables=símismo._gen_vars(tmñ_ciclo))

    @staticmethod
    def _gen_vars(tmñ_ciclo):
        return VariablesModDeter([
            Variable('ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            VarPasoDeter('paso', unid=None, ingr=False, egr=True, tmñ_ciclo=tmñ_ciclo, líms=(0, None)),
            VarPasoDeter(
                'i_en_ciclo', unid=None, ingr=False, egr=True, inic=tmñ_ciclo - 1, tmñ_ciclo=tmñ_ciclo, líms=(0, None)
            ),
            VarPasoDeter('ingreso_paso', unid=None, ingr=True, egr=False, tmñ_ciclo=tmñ_ciclo, líms=(0, None)),
            Variable('ingreso_ciclo', unid=None, ingr=True, egr=False, líms=(None, None))
        ])

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def avanzar_modelo(símismo, n_ciclos):
        símismo.variables['ciclo'] += n_ciclos
        paso = símismo.variables['paso'].obt_val()
        símismo.variables['paso'].poner_vals_paso(np.arange(paso + 1, paso + símismo.tmñ_ciclo + 1))
        símismo.variables['i_en_ciclo'].poner_vals_paso(np.arange(símismo.tmñ_ciclo))


class EjBloques(ModeloBloques):

    def __init__(símismo, tmñ_bloques, unid_tiempo='días'):
        símismo.unid_tiempo = unid_tiempo

        super().__init__(variables=símismo._gen_vars(tmñ_bloques))

    @staticmethod
    def _gen_vars(tmñ_bloques):
        # noinspection PyTypeChecker
        tmñ_ciclo = np.sum(tmñ_bloques)  # type: int
        return VariablesModBloques([
            Variable('ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            VarBloque(
                'bloque', unid=None, ingr=False, egr=True, tmñ_bloques=tmñ_bloques, inic=len(tmñ_bloques) - 1,
                líms=(0, None)
            ),
            VarPasoDeter('paso', unid=None, ingr=False, egr=True, tmñ_ciclo=tmñ_ciclo, líms=(0, None)),
            VarPasoDeter(
                'i_en_ciclo', unid=None, ingr=False, egr=True, tmñ_ciclo=tmñ_ciclo, inic=tmñ_ciclo - 1, líms=(0, None),
            ),
            Variable('ingreso_ciclo', unid=None, ingr=True, egr=False, líms=(0, None)),
            VarPasoDeter('ingreso_paso', unid=None, ingr=True, egr=False, tmñ_ciclo=tmñ_ciclo, líms=(0, None)),
            VarBloque('ingreso_bloque', unid=None, ingr=True, egr=False, tmñ_bloques=tmñ_bloques, líms=(0, None))
        ], tmñ_bloques=tmñ_bloques)

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def avanzar_modelo(símismo, n_ciclos):
        símismo.variables['ciclo'] += n_ciclos
        paso = símismo.variables['paso'].obt_val()
        símismo.variables['paso'].poner_vals_paso(np.arange(paso + 1, paso + símismo.tmñ_ciclo + 1))
        símismo.variables['i_en_ciclo'].poner_vals_paso(np.arange(símismo.tmñ_ciclo))
        símismo.variables['bloque'].poner_vals_paso(np.arange(len(símismo.variables.tmñ_bloques)))


class EjIndeterminado(ModeloIndeterminado):

    def __init__(símismo, rango_n, unid_tiempo='días'):
        símismo.rango_n = rango_n
        símismo.unid_tiempo = unid_tiempo

        super().__init__(variables=símismo._gen_vars())

    @staticmethod
    def _gen_vars():
        return VariablesModIndeterminado([
            Variable('ciclo', unid=None, ingr=False, egr=True, líms=(0, None)),
            VarPasoIndeter('paso', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('ingreso', unid=None, ingr=True, egr=False, líms=(0, None))
        ])

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def mandar_modelo(símismo):
        n = np.random.randint(*símismo.rango_n)
        símismo.variables['ciclo'] += 1
        paso = símismo.variables['paso'].obt_val()
        símismo.variables['paso'].poner_vals_paso(np.arange(paso + 1, n + paso + 1))
        return n
