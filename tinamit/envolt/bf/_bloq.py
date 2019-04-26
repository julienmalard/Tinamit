import numpy as np

from tinamit.envolt.bf._deter import ModeloDeterminado, VariablesModDeter, VarPasoDeter


class ModeloBloques(ModeloDeterminado):

    def __init__(símismo, variables, nombre='bf'):
        """

        Parameters
        ----------
        variables: VariablesModBloques
        nombre: str
        """
        super().__init__(tmñ_ciclo=np.sum(variables.tmñ_bloques), variables=variables, nombre=nombre)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError


class VariablesModBloques(VariablesModDeter):

    def __init__(símismo, variables, tmñ_bloques):
        símismo.tmñ_bloques = tmñ_bloques
        símismo.tmñ_bloques_cum = np.cumsum(tmñ_bloques)
        símismo.n_bloques = len(tmñ_bloques)
        super().__init__(variables)

    def act_paso(símismo, paso):
        b = símismo.bloque(paso)
        for v in símismo.vars_paso():
            if isinstance(v, VarBloque):
                v.act_paso(b)
            else:
                v.act_paso(paso)

    def bloque(símismo, paso):
        return next(i for i, s in enumerate(símismo.tmñ_bloques_cum) if paso < s)


class VarBloque(VarPasoDeter):

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_bloques, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, tmñ_ciclo=len(tmñ_bloques), inic=inic, líms=líms, info=info)
