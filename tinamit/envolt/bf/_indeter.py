from ._impac import ModeloImpaciente, VarPaso, VariablesModImpaciente


class ModeloIndeterminado(ModeloImpaciente):
    """
    La clase pariente para todos modelos que avanzan por un número indeterminado de pasos a cada corrida.
    """

    def __init__(símismo, variables, nombre='bf'):
        super().__init__(tmñ_ciclo=1, variables=variables, nombre=nombre)

    def incrementar(símismo, rebanada):
        # Para simplificar el código un poco.
        p = símismo.paso_en_ciclo

        # Aplicar el incremento de paso
        p += rebanada.n_pasos

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        while p >= símismo.tmñ_ciclo:
            p -= símismo.tmñ_ciclo

            # Avanzar la simulación
            símismo.tmñ_ciclo = símismo.mandar_modelo()

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = p

        # Actualizar el paso en los variables
        símismo.variables.act_paso(símismo.paso_en_ciclo)

        super().incrementar(rebanada)

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def mandar_modelo(símismo):
        raise NotImplementedError


class VariablesModIndeterminado(VariablesModImpaciente):
    """
    Representa los variables de un modelo :class:`~tinamit.envolt.bf._indeter.ModeloIndeterminado`.
    """
    pass


class VarPasoIndeter(VarPaso):
    """
    Representa un variable de un modelo :class:`~tinamit.envolt.bf._indeter.ModeloIndeterminado` cuyo valor
    cambia a cada paso (y no solamente a cada ciclo).
    """

    def __init__(símismo, nombre, unid, ingr, egr, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, tmñ_ciclo=1, inic=inic, líms=líms, info=info)

    def poner_vals_paso(símismo, val, paso=None):
        # para hacer: ¿incecesario reimplementar esta función?        
        símismo._matr_paso = val
