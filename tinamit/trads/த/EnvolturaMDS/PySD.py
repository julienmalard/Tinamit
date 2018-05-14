from tinamit.EnvolturaMDS.PySD import ModeloPySD


class ModeloPySD(ModeloPySD):

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()
