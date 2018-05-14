from tinamit.BF import ModeloFlexible
from tinamit.BF import ModeloImpaciente
from tinamit.BF import ModeloBF
from tinamit.BF import EnvolturaBF


class EnvolturaBF(EnvolturaBF):

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def paralelizable(símismo):
        return super().paralelizable()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloBF(ModeloBF):

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

    def leer_vals_inic(símismo):
        return super().leer_vals_inic()

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloImpaciente(ModeloImpaciente):

    def act_vals_clima(தன், படி_எண், தேதி):
        return super().act_vals_clima(n_paso=படி_எண், f=தேதி)

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

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

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()


class ModeloFlexible(ModeloFlexible):

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()

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

    def unidad_tiempo(símismo):
        return super().unidad_tiempo()
