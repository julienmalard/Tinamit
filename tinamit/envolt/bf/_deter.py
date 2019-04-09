import math as mat

from ._impac import ModeloImpaciente


class ModeloDeterminado(ModeloImpaciente):

    def incrementar(símismo, corrida):
        # Para simplificar el código un poco.
        p = símismo.paso_en_ciclo
        n_pasos = corrida.eje_tiempo.pasos_avanzados(símismo.unidad_tiempo())
        í = corrida.eje_tiempo.í

        # Aplicar el incremento de paso
        p_después = (p + n_pasos) % símismo.tmñ_ciclo

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = p_después

        # Actualizar el paso en los variables
        símismo.variables.act_paso(símismo.paso_en_ciclo)

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        if p == 0 or (p_después < p and (p_después >= 1)):
            # El número de ciclos para simular
            c = mat.ceil(n_pasos / símismo.tmñ_ciclo)  # type: int
            símismo.ciclo += c

            # Avanzar la simulación
            símismo.avanzar_modelo(n_ciclos=c)

    def avanzar_modelo(símismo, n_ciclos):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def _gen_vars(símismo):
        raise NotImplementedError
