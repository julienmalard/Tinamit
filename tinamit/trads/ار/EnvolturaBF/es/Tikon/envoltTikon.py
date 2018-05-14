from tinamit.EnvolturaBF.es.Tikon.envoltTikon import ModeloTikon


class ModeloTikon(ModeloTikon):

    def escribir_archivo_ingr(خود, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_archivo_vals_inic(خود):
        return super().leer_archivo_vals_inic()

    def act_vals_clima(خود, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def leer_archivo_egr(خود, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def iniciar_modelo(خود, tiempo_final, nombre_corrida):
        return super().iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida)

    def avanzar_modelo(خود):
        return super().avanzar_modelo()

    def cerrar_modelo(خود):
        return super().cerrar_modelo()
