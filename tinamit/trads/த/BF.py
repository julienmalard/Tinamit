from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente
from tinamit.BF import ModeloBF
from tinamit.BF import EnvolturaBF


class EnvolturaBF(EnvolturaBF):

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()


class ModeloBF(ModeloBF):

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()


class ModeloImpaciente(ModeloImpaciente):

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(தன், படி_எண், f):
        return super().act_vals_clima(n_paso=படி_எண், f=f)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def avanzar_modelo(தன்):
        return super().avanzar_modelo()

    def leer_vals_inic(தன்):
        return super().leer_vals_inic()

    def leer_archivo_vals_inic(தன்):
        return super().leer_archivo_vals_inic()

    def leer_egr(தன், n_años_egr):
        return super().leer_egr(n_años_egr=n_años_egr)

    def escribir_ingr(தன், n_años_simul):
        return super().escribir_ingr(n_años_simul=n_años_simul)

    def leer_archivo_egr(தன், n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)


class ModeloFlexible(ModeloFlexible):

    def cambiar_vals_modelo_interno(தன், valores):
        return super().cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(தன்):
        return super().obt_unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்.inic_vars()

    def leer_archivo_vals_inic(தன்):
        return super().leer_archivo_vals_inic()

    def mandar_simul(தன்):
        return super().mandar_simul()

    def leer_archivo_egr(தன், n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)
