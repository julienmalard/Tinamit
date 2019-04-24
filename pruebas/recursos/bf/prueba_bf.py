from tinamit.envolt.bf import ModeloBF
from tinamit.mod import VariablesMod, Variable


class PruebaBF(ModeloBF):

    def __init__(símismo, unid_tiempo='mes', nombre='bf'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars(unid_tiempo))

    @staticmethod
    def _gen_vars(unid_t):
        return VariablesMod([
            Variable('Lluvia', unid='m3/'+unid_t, ingr=False, egr=True, inic=1, líms=(0, None)),
            Variable('Lago', unid='m3', ingr=True, egr=False, inic=1000, líms=(0, None)),
        ])

    def incrementar(símismo, rebanada):
        lago = símismo.variables['Lago'].obt_val()
        símismo.variables['Lluvia'].poner_val(lago / 120 * rebanada.n_pasos)
        super().incrementar(rebanada)

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def paralelizable(símismo):
        return True
