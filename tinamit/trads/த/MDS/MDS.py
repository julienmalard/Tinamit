from tinamit.MDS.MDS import leer_egr_mds
from tinamit.MDS.MDS import generar_mds
from tinamit.MDS.MDS import comanda_vensim
from tinamit.MDS.MDS import ModeloVensim
from tinamit.MDS.MDS import EnvolturaMDS


class EnvolturaMDS(EnvolturaMDS):

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(தன், பாவனைப்பெயர், கடைசி_நேரம்):
        return super().iniciar_modelo(nombre_corrida=பாவனைப்பெயர், tiempo_final=கடைசி_நேரம்)

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def leer_resultados_mds(தன், corrida, var):
        return super().leer_resultados_mds(corrida=corrida, var=var)


class ModeloVensim(ModeloVensim):

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(தன், கடைசி_நேரம், பாவனைப்பெயர்):
        return super().iniciar_modelo(tiempo_final=கடைசி_நேரம், nombre_corrida=பாவனைப்பெயர்)

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def verificar_vensim(தன்):
        return super().verificar_vensim()
