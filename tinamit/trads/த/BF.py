from tinamit.BF import EnvolturaBF
from tinamit.BF import ModeloBF
from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente


class EnvolturaBF(EnvolturaBF):

    def obt_unidad_tiempo(தன்):
        return super().unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்._inic_dic_vars()

    def cambiar_vals_modelo_interno(தன், valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def paralelizable(símismo):
        return super().paralelizable()


class ModeloBF(ModeloBF):

    def cambiar_vals_modelo_interno(தன், valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def incrementar(தன், படி):
        return super().incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(தன்):
        return super().unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்._inic_dic_vars()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()


class ModeloImpaciente(ModeloImpaciente):

    def cambiar_vals_modelo_interno(தன், valores):
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def act_vals_clima(தன், படி_எண், தேதி):
        return super().act_vals_clima(n_paso=படி_எண், f=தேதி)

    def முன்னெடுக்க(தன், படி):
        return தன்.incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def obt_unidad_tiempo(தன்):
        return super().unidad_tiempo()

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்._inic_dic_vars()

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
        return super()._cambiar_vals_modelo_interno(valores=valores)

    def முன்னெடுக்க(தன், படி):
        return தன்.incrementar(paso=படி)

    def leer_vals(தன்):
        return super().leer_vals()

    def iniciar_modelo(தன்):
        return super().iniciar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def obt_unidad_tiempo(தன்):
        return super().unidad_tiempo()

    def மாறிகளை_ஆரம்ப(தன்):
        return தன்._inic_dic_vars()

    def leer_archivo_vals_inic(தன்):
        return super().leer_archivo_vals_inic()

    def mandar_simul(தன்):
        return super().mandar_simul()

    def leer_archivo_egr(தன், n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()
