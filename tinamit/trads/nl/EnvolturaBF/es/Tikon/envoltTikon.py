from tinamit.EnvolturaBF.es.Tikon.envoltTikon import ModeloTikon


class ModeloTikon(ModeloTikon):

    def escribir_archivo_ingr(símismo, n_años_simul, dic_ingr):
        return super().escribir_archivo_ingr(n_años_simul=n_años_simul, dic_ingr=dic_ingr)

    def leer_archivo_vals_inic(símismo):
        return super().leer_archivo_vals_inic()

    def act_vals_clima(símismo, n_paso, f):
        return super().act_vals_clima(n_paso=n_paso, f=f)

    def leer_archivo_egr(símismo, n_años_egr):
        return super().leer_archivo_egr(n_años_egr=n_años_egr)

    def inic_vars(símismo):
        return super()._inic_dic_vars()

    def iniciar_modelo(símismo):
        return super().iniciar_modelo()

    def avanzar_modelo(símismo):
        return super().avanzar_modelo()

    def cerrar_modelo(símismo):
        return super().cerrar_modelo()
