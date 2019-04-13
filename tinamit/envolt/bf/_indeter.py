from ._impac import ModeloImpaciente


class ModeloIndeterminado(ModeloImpaciente):
    def incrementar(símismo, corrida):
        # Para simplificar el código un poco.
        p = símismo.paso_en_ciclo
        n_pasos = corrida.eje_tiempo.pasos_avanzados(símismo.unidad_tiempo())

        # Aplicar el incremento de paso
        p += n_pasos

        # Guardar el pasito actual para la próxima vez.
        símismo.paso_en_ciclo = p

        # Actualizar el paso en los variables
        símismo.variables.act_paso(símismo.paso_en_ciclo)

        # Si hay que avanzar el modelo externo, lanzar una su simulación aquí.
        while p >= símismo.tmñ_ciclo:

            p -= símismo.tmñ_ciclo

            # Avanzar la simulación
            símismo.tmñ_ciclo = símismo.mandar_modelo()

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError

    def mandar_modelo(símismo):
        raise NotImplementedError

