from tinamit.EnvolturaBF.es.Tikon.envoltTikon import ModeloTikon


class ModeloTikon(ModeloTikon):

    def escribir_archivo_ingr(தன், n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_archivo_vals_inic(தன்):
        return super().leer_archivo_vals_inic()

    def act_vals_clima(தன், படி_எண், தேதி):
        return super().act_vals_clima(n_paso=படி_எண், f=தேதி)

    def leer_archivo_egr(தன், n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def iniciar_modelo(தன், tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def avanzar_modelo(தன்):
        return super().avanzar_modelo()

    def cerrar_modelo(தன்):
        return super().cerrar_modelo()
