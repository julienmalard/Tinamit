from tinamit.envolt.bf import EnvolturaBF
from tinamit.mod import VariablesMod, Variable


class ModeloPrueba(EnvolturaBF):

    def __init__(símismo, unid_tiempo='años', nombre='modeloBF'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    @staticmethod
    def _gen_vars():
        return VariablesMod([
            Variable('Lluvia', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('Lago', unid=None, ingr=True, egr=False, líms=(0, None)),
        ])

    def incrementar(símismo, corrida):
        lago = símismo.variables['Lago'].obt_val()
        símismo.variables['Lluvia'].poner_val(lago / 10 * paso)

    def cerrar(símismo):
        pass

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def _vals_inic(símismo):
        return {'Lluvia': 1, 'Lago': 1000, 'Escala': 0, 'Vacío': 10, 'Vacío2': 10, 'Vacío3': 10, 'Aleatorio': 0}

    def paralelizable(símismo):
        return True
