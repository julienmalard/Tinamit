from tinamit.envolt.bf import EnvolturaBF
from tinamit.mod import VariablesMod, Variable


class ModeloPrueba(EnvolturaBF):

    def __init__(símismo, unid_tiempo='años', nombre='bf'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    @staticmethod
    def _gen_vars():
        return VariablesMod([
            Variable('Lluvia', unid=None, ingr=False, egr=True, inic=1, líms=(0, None)),
            Variable('Lago', unid=None, ingr=True, egr=False, inic=1000, líms=(0, None)),
        ])

    def incrementar(símismo, rebanada):
        super().incrementar(rebanada)
        lago = símismo.variables['Lago'].obt_val()
        símismo.variables['Lluvia'].poner_val(lago / 10 * rebanada.n_pasos)

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def paralelizable(símismo):
        return True
