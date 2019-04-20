from tinamit.mod import VariablesMod, Variable, Modelo


class ModeloPrueba(Modelo):

    def __init__(símismo, unid_tiempo='años', nombre='prueba'):
        símismo.unid_tiempo = unid_tiempo
        super().__init__(nombre=nombre, variables=símismo._gen_vars())

    def incrementar(símismo):
        super().incrementar()
        vars_ = símismo.corrida.variables
        pasos = símismo.corrida.t.pasos_avanzados(símismo.unidad_tiempo())
        vars_.cambiar_vals({
            'Escala': vars_['Escala'].obt_val() + pasos,
        })

    @staticmethod
    def _gen_vars():
        return VariablesMod([
            Variable('Escala', unid=None, ingr=False, egr=True, líms=(0, None)),
            Variable('Vacío', unid=None, ingr=True, egr=False, líms=(0, None)),
            Variable('Vacío2', unid=None, ingr=True, egr=False, líms=(0, None), inic=[0, 0]),
        ])

    def unidad_tiempo(símismo):
        return símismo.unid_tiempo

    def paralelizable(símismo):
        return True
