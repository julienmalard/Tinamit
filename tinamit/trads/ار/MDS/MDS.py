from tinamit.MDS.MDS import leer_egr_mds
from tinamit.MDS.MDS import generar_mds
from tinamit.MDS.MDS import comanda_vensim
from tinamit.MDS.MDS import ModeloVensim
from tinamit.MDS.MDS import EnvolturaMDS


class EnvolturaMDS(EnvolturaMDS):

    def inic_vars(خود):
        return super().inic_vars()

    def obt_unidad_tiempo(خود):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(خود, nombre_corrida, tiempo_final):
        return super().iniciar_modelo(nombre_corrida=nombre_corrida, tiempo_final=tiempo_final)

    def cambiar_vals_modelo_interno(خود, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def leer_resultados_mds(خود, corrida, var):
        return super().leer_resultados_mds(corrida=corrida, var=var)


class ModeloVensim(ModeloVensim):

    def inic_vars(خود):
        return super().inic_vars()

    def obt_unidad_tiempo(خود):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cambiar_vals_modelo_interno(خود, valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(خود, قدم):
        return super().incrementar(paso=قدم)

    def leer_vals(خود):
        return super().leer_vals()

    def cerrar_modelo(خود):
        return super().cerrar_modelo()

    def verificar_vensim(خود):
        return super().verificar_vensim()
