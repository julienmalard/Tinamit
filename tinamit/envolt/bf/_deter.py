import math as mat

from ._impac import ModeloImpaciente, VariablesModImpaciente, VarPaso


class ModeloDeterminado(ModeloImpaciente):

    def incrementar(símismo, rebanada):
        # Para simplificar el código un poco.
        p = símismo.paso_en_ciclo
        n_pasos = rebanada.n_pasos

        # Aplicar el incremento de paso
        p_después = (p + n_pasos) % símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = p_después

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if p_después == 0 or ((p + n_pasos) >= símismo.tmñ_ciclo):
            # El número de ciclos para simular
            c = mat.ceil(n_pasos / símismo.tmñ_ciclo)  # type: int

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

        # Actualizar el paso en los variables
        símismo.variables.act_paso(símismo.paso_en_ciclo)

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError


class VariablesModDeter(VariablesModImpaciente):
    pass


class VarPasoDeter(VarPaso):

    def __init__(símismo, nombre, unid, ingr, egr, tmñ_ciclo, inic=0, líms=None, info=''):
        super().__init__(nombre, unid, ingr, egr, tmñ_ciclo=tmñ_ciclo, inic=inic, líms=líms, info=info)
