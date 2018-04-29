from tinamit.EnvolturaMDS import leer_egr_mds
from tinamit.EnvolturaMDS import generar_mds
from tinamit.EnvolturaMDS import comanda_vensim
from tinamit.EnvolturaMDS import ModeloVensim
from tinamit.EnvolturaMDS import EnvolturaMDS


class EnvolturaMDS(EnvolturaMDS):

    def inic_vars(símismo):
        return super().inic_vars()

    def obt_unidad_tiempo(símismo):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(símismo, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def leer_resultados_mds(símismo, corrida, var):
        return super().leer_resultados_mds(corrida=corrida, var=var)


class ModeloVensim(ModeloVensim):

    def inic_vars(símismo):
        return super().inic_vars()

    def obt_unidad_tiempo(símismo):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(símismo, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cambiar_vals_modelo_interno(símismo, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(símismo, paso):
        return super().incrementar(paso=paso)

    def leer_vals(símismo):
        return super().leer_vals()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()

    def verificar_vensim(símismo):
        return super().verificar_vensim()
